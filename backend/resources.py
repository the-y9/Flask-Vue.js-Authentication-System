from flask_restful import Resource, Api, reqparse, marshal_with, fields
from flask_security import auth_required, roles_required, current_user
from backend.models import db
from sqlalchemy import func
from flask import jsonify, request
from .instance import cache
from .models import User, Projects, Milestones, Notifications, Team, TeamMembers, NotificationUser
import requests
from datetime import datetime
from .other_api import other_api_bp
import google.generativeai as genai
import pandas as pd
import json
import re
# GOOGLE_API_KEY = 'AIzaSyBXWPw2U4D1DuOtEDRLrCBcNxnb1qlBh30'
# genai.configure(api_key=GOOGLE_API_KEY)


api = Api()


class Project_Manager(Resource):
    
    # Get a specific milestone by ID
    def get(self, id=None,project_id=None):
        if id:
            try:
                milestone = Milestones.query.get(id)
                if milestone:
                    return jsonify({
                        'id': milestone.id,
                        'project_id': milestone.project_id,
                        'task_no': milestone.task_no,
                        'task': milestone.task,
                        'description': milestone.description,
                        'deadline': milestone.deadline
                    })
                return jsonify({'message': 'Milestone not found'})
            except Exception as e:
                return jsonify({'ERROR': f'{e}'})

    # Get all milestones for a specific project
    
        elif project_id:
            project = Projects.query.filter_by(id=project_id).first()
            milestones = Milestones.query.filter_by(project_id=project_id).all()
            if milestones:
                return jsonify({
                    'id': project.id,
                    'name': project.title,
                    'description': project.description,
                    'startDate': project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
                    'endDate': project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
                    'milestones':
                    [{
                    'id': milestone.id,
                    'task_no': milestone.task_no,
                    'taskName': milestone.task,
                    'description': milestone.description,
                    'deadline': milestone.deadline
                } for milestone in milestones]})
            return jsonify({'message': 'Milestones not found for the project'})
        

        '''{
                id: 2,
                name: 'Project Beta',
                teams: [{ id: 3, name: 'Team C' }],
                startDate: '2024-03-01',
                endDate: '2024-08-15',
                milestones: [
                    { id: 201, name: 'Milestone 1', status: 'Pending' }
                ]
            }
        '''
        # Case 2: Get all projects
        all_projects = Projects.query.all()  # Retrieve all projects from the database

        if all_projects:
            result = []
            
            for project in all_projects:
                # Get teams related to the project
                teams = [
                    {'id': team.id, 'name': team.name, 'repo_owner': team.repo_owner, 'repo_name': team.repo_name} for team in Team.query.filter_by(project_id=project.id).all()
                ]
                
                # Get milestones related to the project
                milestones = [
                    {'id': milestone.id, 'name': milestone.task, 'status': 'Pending'} for milestone in Milestones.query.filter_by(project_id=project.id).all()
                ]
                
                # Add project data to the result list
                result.append({
                    'id': project.id,
                    'name': project.title,
                    'teams': teams,
                    'startDate': project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
                    'endDate': project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
                    'milestones': milestones
                })
            
            # print(result[0])
            return jsonify(result)

        # Return message if no projects found
        return jsonify({'message': 'No projects found'})

    # Create a new
    @roles_required('instructor')
    def post(self):
        data = request.get_json()

        if 'title' in data:
            # Check if the project already exists
            existing_project = Projects.query.filter_by(title=data['title']).first()
            if existing_project:
                return jsonify({'message': 'Project with this title already exists'})

            # Create a new project
            new_project = Projects(
                title=data['title'],
                description=data.get('description', ''),  # Default to empty string if description is not provided
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d') if 'start_date' in data else None,
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d') if 'end_date' in data else None
            )
            db.session.add(new_project)
            db.session.commit()

            return {
                'id': new_project.id,
                'title': new_project.title,
                'description': new_project.description,
                'start_date' : new_project.start_date.strftime('%Y-%m-%d %H:%M:%S') if new_project.start_date else None,
                'end_date' : new_project.end_date.strftime('%Y-%m-%d %H:%M:%S') if new_project.end_date else None
            }

        # Case 2: Create a new milestone
        elif 'project_id' in data and 'milestones' in data:
            project = Projects.query.get(data['project_id'])
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            milestones = data["milestones"]
            new_milestones = []
            for index, milestone in enumerate(milestones):
                new_milestone = Milestones(
                    project_id=data['project_id'],
                    task_no=index+1,
                    task=milestone['task'],
                    description=milestone.get('description', ''),
                    deadline=datetime.strptime(milestone['deadline'], '%Y-%m-%d') if 'deadline' in milestone else None
                )
                db.session.add(new_milestone)
                new_milestones.append(new_milestone)

            db.session.commit()

            serialized_milestones = [
                        {
                            'task_no': m.task_no,
                            'task': m.task,
                            'description': m.description,
                            'deadline': m.deadline.strftime('%Y-%m-%d %H:%M:%S') if m.deadline else None
                        }
                        for m in new_milestones
            ]
            return {
                'project_id': project.id,
                'milestones': serialized_milestones
            }

        # Case 3: Invalid request (missing required fields)
        return jsonify({'message': 'Invalid data for creating project or milestone'})


    # Delete a milestone
    @roles_required('instructor')
    def delete(self, id=None,project_id=None):
        if id:
            milestone = Milestones.query.get(id)
            if not milestone:
                return jsonify({'message': 'Milestone not found'})

            db.session.delete(milestone)
            db.session.commit()
            return jsonify({'message': 'Milestone deleted successfully'})
        # return {'message': 'ID is required to delete a milestone'}, 400
    
    # Delete a project
    
        if project_id:
            project = Projects.query.filter_by(id=project_id).first()
            
            if not project:
                return jsonify({'message': 'project not found'})

            db.session.delete(project)
            db.session.commit()
            return jsonify({'message': 'project deleted successfully'})
        return {'message': 'ID is required to delete. '}

    @roles_required('instructor')
    def put(self, id=None):
        data = request.get_json()

        # Update a milestone
        if id:
            milestone = Milestones.query.get(id)
            if not milestone:
                return jsonify({'message': 'Milestone not found'})
            print(4, id, data, milestone)
            # Update milestone fields
            milestone.task_no = data.get('task_no', milestone.task_no)
            milestone.task = data.get('taskName', milestone.task)
            milestone.description = data.get('description', milestone.description)
            if 'deadline' in data:
                try:
                    print(5, id, data, datetime.strptime(data['deadline'], '%a, %d %b %Y %H:%M:%S %Z'))
                    milestone.deadline = datetime.strptime(data['deadline'], '%a, %d %b %Y %H:%M:%S %Z')
                    print(7)
                except ValueError:
                    return jsonify({'message': 'Invalid deadline format. Use YYYY-MM-DD HH:MM:SS'})
            
            print(6, milestone.deadline)
            db.session.commit()
            return jsonify({
                'id': milestone.id,
                'task_no': milestone.task_no,
                'task': milestone.task,
                'description': milestone.description,
                'deadline': milestone.deadline.strftime('%Y-%m-%d %H:%M:%S') if milestone.deadline else None
            })

        # Invalid request
        return jsonify({'message': 'Invalid request. Provide a milestone ID to update.'})

# Add resources to the API with different routes
api.add_resource(Project_Manager, '/projects','/project','/projects/<int:project_id>', '/milestone', '/milestone/<int:id>', '/project/<int:project_id>/milestones')

class Notification_Manager(Resource):
    # @roles_required('instructor')
    def get(self, id=None, user_id=None):
        if id:
            try:
                notification = Notifications.query.get(id)
                if notification:
                    return jsonify({
                        'id': notification.id,
                        'title': notification.title,
                        'message': notification.message,
                        'created_at': notification.created_at
                    }), 200
                return jsonify({'message': 'Notification not found'})
            except Exception as e:
                return jsonify({'ERROR': f'{e}'})
        
        elif user_id:
            notifications = Notifications.query.filter_by(created_for=user_id).all()
            
            if notifications:
                notification_list = [{
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message
                } for notification in notifications]
                return notification_list, 200
            return jsonify({'message': 'No notifications found for this team'})

        return {'message': 'Team ID or Notification ID is required'}
    
    def post(self):
        data = request.get_json()

        # Ensure required fields are present
        if not all(key in data for key in ['notificationTitle', 'notificationMessage']):
            return jsonify({'message': 'Missing required fields'})

        try:
            if 'teamId' in data and data['teamId']:
                # Add notification for all team members
                team_members = TeamMembers.query.filter_by(team_id=data['teamId']).all() 
                if not team_members:
                    return jsonify({'message': 'No members found for the specified team.'})

                notifications = []
                for member in team_members:
                    notification = Notifications(
                        title=data['notificationTitle'],
                        message=data['notificationMessage'],
                        created_for=member.user_id,
                        created_by=data['instructorId']
                    )
                    db.session.add(notification)
                    notifications.append(notification)

                db.session.commit()

                notification_users = []
                for notification in notifications:
                    notification_user = NotificationUser(
                        notification_id=notification.id,
                        user_id=notification.created_for
                    )
                    db.session.add(notification_user)
                    notification_users.append(notification_user)

                db.session.commit()
                notification_user = NotificationUser(
                                notification_id=new_notification.id,
                                user_id=new_notification.created_for
                            )
                db.session.add(notification_user)
                db.session.commit()

                notification_data = [
                    {
                        'id': notification.id,
                        'title': notification.title,
                        'message': notification.message,
                        'created_for': notification.created_for,
                        'created_by': notification.created_by,
                        'created_at': notification.created_at
                    }
                    for notification in notifications
                ]

                return jsonify({'message': 'Notifications created successfully for all team members.', 'data': notification_data})

            elif 'memberId' in data and data['memberId']:
                # Add notification for a specific member
                new_notification = Notifications(
                    title=data['notificationTitle'],
                    message=data['notificationMessage'],
                    created_for=data['memberId'],  # No team ID if it's specific to a member
                    created_by=data['instructorId']
                )
                db.session.add(new_notification)
                db.session.commit()

                notification_data = {
                    'id': new_notification.id,
                    'title': new_notification.title,
                    'message': new_notification.message,
                    'created_for': new_notification.created_for,
                    'created_by': new_notification.created_by,
                    'created_at': new_notification.created_at
                }

                return jsonify({'message': 'Notification created successfully for the member.', 'data': notification_data})

            else:
                return jsonify({'message': 'Either teamId or memberId must be provided.'})

        except Exception as e:
            return jsonify({'ERROR': f'{e}'})
        
    @roles_required('instructor')
    def delete(self, id=None):
        if id:
            notification = Notifications.query.get(id)
            if not notification:
                return jsonify({'message': 'Notification not found'})

            db.session.delete(notification)
            db.session.commit()
            return jsonify({'message': 'Notification deleted successfully'})

        return jsonify({'message': 'Notification ID is required to delete a notification'})

api.add_resource(
    Notification_Manager,
    '/notifications',  # For creating a new notification (POST)
    '/notifications/<int:id>',  # For fetching or deleting a specific notification by ID (GET/DELETE)
    '/notifications/user/<int:user_id>'  # For fetching all notifications for a specific user (GET)
)

class ProjectUpdate(Resource):
    # Update a specific project
    @roles_required('instructor')
    def put(self, project_id=None):
        data = request.get_json()

        # Update a project
        if project_id:
            project = Projects.query.get(project_id)
            if not project:
                return jsonify({'message': 'Project not found'})

            # Update project fields
            project.title = data.get('name', project.title)
            project.description = data.get('description', project.description)
            if 'startDate' in data:
                try:
                    project.start_date = datetime.strptime(data['startDate'], '%Y-%m-%d')
                except ValueError:
                    return jsonify({'message': 'Invalid start_date format. Use YYYY-MM-DD'})

            if 'endDate' in data:
                try:
                    project.end_date = datetime.strptime(data['endDate'], '%Y-%m-%d')
                except ValueError:
                    return jsonify({'message': 'Invalid end_date format. Use YYYY-MM-DD'})

            db.session.commit()
            return {
                'id': project.id,
                'name': project.title,
                'description': project.description,
                'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
                'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else None
            }, 200

        # Invalid request
        return jsonify({'message': 'Invalid request. Provide a project ID to update.'})
    
api.add_resource(ProjectUpdate,'/projects/update/<int:project_id>')
