# from celery import Celery
from backend.models import Notifications, db
from datetime import datetime, timedelta
from flask import current_app as app, jsonify, request, Blueprint, send_from_directory
from flask_security import roles_required
from flask_restful import Resource, Api, reqparse, marshal_with, fields
from .models import User, db, Projects, Milestones,Team, TeamMembers, EvaluationCriteria, PeerReview, SystemLog
import requests
from sqlalchemy import func,case
import google.generativeai as genai
import pandas as pd
import json
import re
GOOGLE_API_KEY = 'AIzaSyBXWPw2U4D1DuOtEDRLrCBcNxnb1qlBh30'
genai.configure(api_key=GOOGLE_API_KEY)


other_api_bp = Blueprint('other_api', __name__)

'''have to Replace https://genai-model.example.com/ with actual GenAI model URLs or APIs.
'''

api = Api(other_api_bp)

# celery = Celery('tasks', broker='redis://localhost:6379/0')
# @celery.task
def send_reminder_notifications():
    # Find milestones due in 24 hours
    now = datetime.now()
    upcoming_milestones = Milestones.query.filter(
        Milestones.deadline.between(now, now + timedelta(hours=24))
    ).all()

    # Create notifications for each milestone
    for milestone in upcoming_milestones:
        notification = Notifications(
            title=f"Reminder: Upcoming Milestone",
            message=f"Milestone '{milestone.task}' is due on {milestone.deadline}.",
            created_for=milestone.project_id,
            created_by='System'
        )
        db.session.add(notification)

    db.session.commit()
    return "Reminders Sent"

class ReminderManager(Resource):
    def post(self):
        try:
            send_reminder_notifications.apply_async()
            return jsonify({'message': 'Reminder notifications sent successfully'})
        except Exception as e:
            return jsonify({'ERROR': f'{e}'})

api.add_resource(ReminderManager, '/reminders/send')

class SubmissionValidation(Resource):
    @roles_required('student')
    def post(self):
        data = request.get_json()
        required_fields = ['submission', 'project_id', 'milestone_id']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'})

        # Fetch milestone details
        milestone = Milestones.query.get(data['milestone_id'])
        if not milestone:
            return jsonify({'message': 'Milestone not found'})

        # Call the GenAI model for validation
        genai_url = "https://genai-model.example.com/validate"
        payload = {
            "submission": data['submission'],
            "milestone_requirements": milestone.description
        }

        try:
            response = requests.post(genai_url, json=payload)
            if response.status_code == 200:
                validation_result = response.json()
                return jsonify({
                    'validation_result': validation_result,
                    'feedback': validation_result.get('feedback', 'No feedback provided')
                }), 200
            return jsonify({'message': 'Error from GenAI model'}), response.status_code
        except Exception as e:
            return jsonify({'ERROR': f'{e}'})

api.add_resource(SubmissionValidation, '/submission/validate')

class PerformancePrediction(Resource):
    @roles_required('instructor')
    def post(self):
        data = request.get_json()
        if 'students_data' not in data:
            return jsonify({'message': 'Missing students data'})

        # Call GenAI model to analyze performance
        genai_url = "https://genai-model.example.com/predict"
        try:
            response = requests.post(genai_url, json=data)
            if response.status_code == 200:
                prediction_results = response.json()
                return jsonify({'students_needing_support': prediction_results})
            return jsonify({'message': 'Error from GenAI model'})
        except Exception as e:
            return jsonify({'ERROR': f'{e}'}), 500

api.add_resource(PerformancePrediction, '/students/performance-prediction')

class DocumentationChatbot(Resource):
    def post(self):
        data = request.get_json()

        if 'question' not in data or 'api_key' not in data:
            return jsonify({'message': 'Missing question or api_key field'})

        question = data['question']
        api_key = data['api_key']
        prompt = """In course projects such as the ones you have already done in Application Development I and II, it can be challenging for instructors to effectively track the progress of student projects, particularly in larger classes where multiple teams are working on different tasks. To address this issue, you are required to develop a web application that allows instructors to manage and monitor student projects throughout the semester. The system should enable the instructor to break down projects into well-defined milestones, allowing for clearer tracking of progress and deadlines. Key features include integrating with GitHub or similar version control systems to automatically pull and visualize commit histories, ensuring students are on track with their coding progress. Additionally, the application can leverage Generative AI (GenAI) tools to assist instructors by analyzing student-submitted documents, such as project proposals, progress reports, and technical documentation. You can also think of additional features such as providing a centralized dashboard where instructors can see an overview of all students or teams, customizable milestones and task management, using AI to predict if students are on track, etc. These are just a few examples of features; please feel free to add others. """ + question
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            response = model.generate_content(prompt)
            answer = str(response.candidates[0].content.parts[0].text)
            return ({'response': answer}), 200
        
        except Exception as e:
            return jsonify({'ERROR': str(e)})
        
api.add_resource(DocumentationChatbot, '/chatbot/ask')

# will be dited
class TeamPerformance(Resource):
    def get(self):
        try:
            # Aggregate performance data
            teams = db.session.query(
                Team.id.label('team_id'),
                Team.name.label('team_name'),
                func.count(Milestones.id).label('total_milestones'),
                func.sum(
                    case(
                        [
                            (Milestones.deadline < datetime.now(), 1)
                        ], 
                        else_=0
                    )
                ).label('overdue_milestones')
            ).join(TeamMembers, TeamMembers.team_id == Team.id) \
             .join(User, TeamMembers.user_id == User.id) \
             .join(Projects, Projects.id == Team.project_id) \
             .join(Milestones, Milestones.project_id == Projects.id) \
             .group_by(Team.id).all()

            # Prepare response data
            team_data = [{
                'team_id': team[0],
                'team_name': team[1],
                'total_milestones': team[2],
                'overdue_milestones': team[3]
            } for team in teams]

            return jsonify({'teams': team_data})

        except Exception as e:
            return jsonify({'ERROR': f'{e}'})


api.add_resource(TeamPerformance, '/teams/performance')


class InstructorFeedbackNotifications(Resource):
    def get(self, project_id):
        try:
            notifications = Notifications.query.filter_by(created_for=project_id).all()
            
            feedback = [{
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'created_at': notif.created_at
            } for notif in notifications]

            return jsonify({'feedback_notifications': feedback})
        except Exception as e:
            return jsonify({'ERROR': f'{e}'})

api.add_resource(InstructorFeedbackNotifications, '/feedback/<int:project_id>')

# Peer Review: Add Evaluation Criteria
class AddEvaluationCriteria(Resource):
    @roles_required('instructor')
    def post(self, projectId):
        data = request.get_json()
        if 'criteriaList' not in data:
            return jsonify({'message': 'Invalid data format. Please provide a valid criteria list.'})

        try:
            project = Projects.query.get(projectId)
            if not project:
                return jsonify({'message': f'Project with ID {projectId} not found.'})

            criteria_objects = []
            for item in data['criteriaList']:
                criterion = item.get('criterion')
                description = item.get('description', '')
                if not criterion:
                    return jsonify({'message': 'Each criterion must have a name.'})
                criteria_objects.append(EvaluationCriteria(project_id=projectId, criterion=criterion, description=description))

            db.session.add_all(criteria_objects)
            db.session.commit()

            return jsonify({
                'message': 'Evaluation criteria added successfully',
                'projectId': projectId,
                'criteria': [{'id': c.id, 'criterion': c.criterion, 'description': c.description} for c in criteria_objects]
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'An error occurred: {str(e)}'})

api.add_resource(AddEvaluationCriteria, '/project/<int:projectId>/evaluation-criteria')

# Peer Review: Submit Peer Review
class SubmitPeerReview(Resource):
    def post(self):
        data = request.get_json()
        required_fields = ['reviewerId', 'projectId', 'criteria']

        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Invalid request data.'})

        try:
            peer_review = PeerReview(
                reviewer_id=data['reviewerId'],
                project_id=data['projectId'],
                criteria=data['criteria']
            )
            db.session.add(peer_review)
            db.session.commit()

            return jsonify({'message': 'Peer review submitted successfully.', 'reviewId': peer_review.id})

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'An error occurred: {str(e)}'})

api.add_resource(SubmitPeerReview, '/peer-review')

# Peer Review: Retrieve Peer Reviews
class RetrievePeerReviews(Resource):
    def get(self, projectId):
        try:
            reviews = PeerReview.query.filter_by(project_id=projectId).all()
            if not reviews:
                return jsonify({'message': f'No peer reviews found for project ID {projectId}.'})

            return jsonify({
                'projectId': projectId,
                'reviews': [
                    {
                        'reviewerId': review.reviewer_id,
                        'criteria': review.criteria,
                        'created_at': review.created_at
                    } for review in reviews
                ]
            })

        except Exception as e:
            return jsonify({'message': f'An error occurred: {str(e)}'})

api.add_resource(RetrievePeerReviews, '/peer-review/project/<int:projectId>')

# Peer Review: Edit Peer Review
class EditPeerReview(Resource):
    def put(self, reviewId):
        data = request.get_json()
        if 'criteria' not in data:
            return jsonify({'message': 'Invalid request data.'})

        try:
            review = PeerReview.query.get(reviewId)
            if not review:
                return jsonify({'message': 'Peer review not found.'})

            review.criteria = data['criteria']
            db.session.commit()

            return jsonify({'message': 'Peer review updated successfully.'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'An error occurred: {str(e)}'})

api.add_resource(EditPeerReview, '/peer-review/<int:reviewId>')

# Peer Review: Delete Peer Review
class DeletePeerReview(Resource):
    def delete(self, reviewId):
        try:
            review = PeerReview.query.get(reviewId)
            if not review:
                return jsonify({'message': 'Peer review not found.'})

            db.session.delete(review)
            db.session.commit()

            return jsonify({'message': 'Peer review deleted successfully.'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'An error occurred: {str(e)}'})

api.add_resource(DeletePeerReview, '/peer-review/<int:reviewId>')

class RetrieveLogs(Resource):
    def get(self):
        try:
            # Retrieve query parameters
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            severity = request.args.get('severity')

            # Base query
            query = SystemLog.query

            # Add filters if provided
            if start_date:
                query = query.filter(SystemLog.timestamp >= start_date)
            if end_date:
                query = query.filter(SystemLog.timestamp <= end_date)
            if severity:
                query = query.filter(SystemLog.severity.ilike(severity))

            # Execute query
            logs = query.order_by(SystemLog.timestamp.asc()).all()

            # Prepare response
            log_data = [
                {
                    'timestamp': log.timestamp.isoformat(),
                    'severity': log.severity,
                    'message': log.message
                }
                for log in logs
            ]

            return jsonify(log_data)

        except Exception as e:
            return jsonify({'ERROR': str(e)})

api.add_resource(RetrieveLogs, '/logs')

class SearchLogs(Resource):
    def post(self):
        try:
            # Parse request body
            data = request.get_json()

            if not data or 'keyword' not in data:
                return jsonify({'message': 'Keyword is required for searching logs.'})

            keyword = data['keyword']

            # Perform case-insensitive search
            logs = SystemLog.query.filter(SystemLog.message.ilike(f"%{keyword}%")).all()

            # Prepare response
            search_results = [
                {
                    'timestamp': log.timestamp.isoformat(),
                    'severity': log.severity,
                    'message': log.message
                }
                for log in logs
            ]

            return jsonify(search_results)

        except Exception as e:
            return jsonify({'ERROR': str(e)})

api.add_resource(SearchLogs, '/logs/search')

# Path to the directory where PDF files are stored
PDF_DIRECTORY = 'pdfs'

class MilestoneDocument(Resource):
    def get(self, team_id, milestone_id):
        try:
            filename = f'team_{team_id}_milestone_{milestone_id}.pdf'
            return send_from_directory(PDF_DIRECTORY, filename, as_attachment=True)

        except FileNotFoundError:
            return {"message": "Document not found"}

        except Exception as e:
            return {"message": str(e)}


api.add_resource(MilestoneDocument, '/teams/<int:team_id>/milestones/<int:milestone_id>/document')



class GenerateMilestones(Resource):
    @roles_required('instructor')
    def post(self):
        data = request.get_json()

        # Validate input
        if 'projectHeading' not in data or 'projectDescription' not in data:
            return {'message': 'Missing projectHeading or projectDescription'}

        project_heading = data['projectHeading']
        project_description = data['projectDescription']

        # Construct the AI prompt with a sample output
        prompt = f"""
        Generate a list of milestones for the project described below:
        Heading: {project_heading}
        Description: {project_description}

        Output requirements:
        - Provide milestones as a JSON-formatted list
        - Each milestone must have 'task' and 'description' keys
        - Provide 3-5 meaningful milestones for the project

        JSON Format Example:
        [
            {{
                "task": "Milestone 1 Title",
                "description": "Detailed description of milestone 1."
            }},
            {{
                "task": "Milestone 2 Title",
                "description": "Detailed description of milestone 2."
            }}
        ]
        """

        try:
            # Call Generative AI
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            ai_output = response.text.strip()

            # Use regex to extract JSON-like content
            json_match = re.search(r'\[\s*{.*?}\s*(?:,\s*{.*?}\s*)*\]', ai_output, re.DOTALL)
            
            if not json_match:
                return {
                    'ERROR': 'Could not extract JSON content',
                    'raw_output': ai_output
                }

            try:
                # Attempt to parse the extracted JSON
                milestones = json.loads(json_match.group(0))

                # Validate milestones structure
                if not isinstance(milestones, list):
                    raise ValueError("Extracted content is not a list of milestones")

                # Ensure each milestone has required fields
                for milestone in milestones:
                    if not all(key in milestone for key in ['task', 'description']):
                        raise ValueError("Milestone is missing 'task' or 'description' fields")

                # Return the parsed milestones
                return {'milestones': milestones}

            except (json.JSONDecodeError, ValueError) as e:
                return {
                    'ERROR': f'Invalid milestone format: {str(e)}',
                    'raw_output': ai_output
                }

        except Exception as e:
            return {
                'ERROR': f'Failed to generate milestones: {str(e)}',
                'raw_output': ai_output
            }

api.add_resource(GenerateMilestones, '/generate-milestones')


class Chatbot(Resource):
    def post(self):
        try:
            # Query each table separately
            projects = db.session.query(
                Projects.id.label('project_id'),
                Projects.title.label('project_title'),
                Projects.description.label('project_description'),
                Projects.start_date.label('start_date'),
                Projects.end_date.label('end_date')
            ).all()

            milestones = db.session.query(
                Milestones.id.label('milestone_id'),
                Milestones.project_id.label('project_id'),
                Milestones.task_no.label('milestone_task_no'),
                Milestones.task.label('milestone_task'),
                Milestones.description.label('milestone_description'),
                Milestones.deadline.label('milestone_deadline')
            ).all()


    
            # Convert query results into DataFrames
            projects_df = pd.DataFrame([{
                'project_id': p.project_id,
                'project_title': p.project_title,
                'project_description': p.project_description,
                'start_date': p.start_date,
                'end_date': p.end_date

            } for p in projects])

            milestones_df = pd.DataFrame([{
                'milestone_id': m.milestone_id,
                'project_id': m.project_id,
                'milestone_task_no': m.milestone_task_no,
                'milestone_task': m.milestone_task,
                'milestone_description': m.milestone_description,
                'milestone_deadline': m.milestone_deadline
            } for m in milestones])



            # Combine the DataFrames into strings for the prompt
            projects_string = projects_df.to_string(index=False)
            milestones_string = milestones_df.to_string(index=False)


            # Fetch the chat data
            try:
                data = request.get_json()
            except Exception as e:
                print(f"Error Parsing JSON: {e}")
                return {'message': 'Invalid JSON payload.'}

            if not data or 'Chat_History' not in data or 'current_message' not in data:
                return {'message': 'Invalid request format. Include Chat_History and current_message.'}

            chat_history = data.get('Chat_History', [])
            current_message = data['current_message'].strip()

            if not current_message:
                return {'message': 'Current message is empty.'}

            # Construct the AI prompt
            prompt = f"""
            You are a helpful, knowledgeable, and friendly AI assistant. Respond to the user's messages in a conversational tone. Be concise and polite.
            You have access to detailed information about projects, milestones. Use the following data to answer the student's questions accurately and specifically.
            Always answer in the Markdown format only and strictly. Never use html tags in responses.

            Projects Data:
            Always check project start and end date from here.
            {projects_string}



            Milestones Data:
            Always check milestones deadline from here.
            {milestones_string}

            Here is the conversation so far:
            """
            for chat in chat_history:
                prompt += f"User: {chat['User']}\nBot: {chat['bot']}\n"
            prompt += f"User: {current_message}\nBot:"

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            bot_response = response.text.strip()

            if not bot_response or bot_response.lower() in [
                "i don't know.",
                "i'm not sure."
            ]:
                bot_response = "I'm sorry, I didn't understand that. Could you please rephrase?"

            return {'bot_response': bot_response}

        except Exception as e:
            print(f"Error Processing Request: {e}")
            return {
                'ERROR': f'Failed to process chatbot request: {str(e)}'
            }

api.add_resource(Chatbot, '/chatbot')
