import random
import sys
import traceback
from main import app
from backend.security import datastore
from backend.models import db, Role, User, Event, Chatbot, ChatbotArticle, HealthMetric, HealthTracker, Dashboard, Notification
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

with app.app_context():
    db.create_all()

    # Define role data
    roles_data = [
        {"category": "Primary", "name": "coach", "description": "User who teaches and manages health"},
        {"category": "Primary", "name": "member", "description": "User who works on health"},
        {"category": "Secondary", "name": "root", "description": "User who manages the system"},
    ]
    
    # Create roles
    try:
        for role in roles_data:
            datastore.find_or_create_role(
                name=role["name"],
                description=role["description"]
            )   
        print(f"{len(roles_data)} roles created.")
        db.session.commit()
    except Exception as e:
        with open("error_initial_data.txt", "w") as file:
            file.write(f"ERROR: {e}\n")
        print(f"ERROR: {e}")
        sys.exit("Exiting the program due to an exception.\n{e}")

    # Define user data
    users_data = [
        {"email": "root@g.com", "username": "root", "password": "r", "roles": ["root"]},
        {"email": "coach@g.com", "username": "coach", "password": "c", "roles": ["coach"]},
        {"email": "member@g.com", "username": "mem", "password": "m", "roles": ["member"]},
    ]

    # Create users
    try:
        for user in users_data:
            if not datastore.find_user(email=user["email"]):
                datastore.create_user(
                    email=user["email"],
                    username=user.get("username", user["username"]),
                    password=generate_password_hash(user["password"]),
                    roles=user["roles"]
                )
        print(f"{len(users_data)} users created.")
        db.session.commit()

    except Exception as e:
        with open("error_initial_data.txt", "w") as file:
            file.write(f"ERROR: {e}\n")
        print(f"{traceback.format_exc()}\n")
        print(f"ERROR: {e}")
        sys.exit("Exiting the program due to an exception.\n{e}")

    # Events data
    events_data = [
        {"name": "Health Seminar", 
        "description": "A seminar on health management.", 
        "start_date": "2025-03-01 09:00:00", 
        "end_date": "2025-03-01 17:00:00", "created_by": 1},

        {"name": "Wellness Workshop", "description": "Workshop on maintaining wellness.", "start_date": "2025-03-05 09:00:00", "end_date": "2025-03-05 12:00:00", "created_by": 2},
    ]
    
    try:
        for event_data in events_data:
            event = Event(
                name=event_data["name"],
                description=event_data["description"],
                start_date=datetime.strptime(event_data["start_date"], "%Y-%m-%d %H:%M:%S"),
                end_date=datetime.strptime(event_data["end_date"], "%Y-%m-%d %H:%M:%S"),                
                created_by=event_data["created_by"]
            )
            db.session.add(event)
        db.session.commit()
        print(f"{len(events_data)} events created.")
    except Exception as e:
        with open("error_initial_data.txt", "w") as file:
            file.write(f"ERROR: {e}\n")
        print(f"ERROR: {e}")
        sys.exit("Exiting the program due to an exception.\n{e}")
    
    # Chatbot and articles data
    chatbot_data = [
        {"name": "HealthBot", "maintained_by": 2, "is_available": True, "last_updated": datetime.utcnow()},
    ]

    chatbot_article_data = [
        {"chatbot_id": 1, "coach_id": 2, "title": "Health Management Tips", "content": "Here are some health management tips for maintaining a balanced lifestyle."},
    ]

    try:
        for chatbot in chatbot_data:
            chatbot_instance = Chatbot(
                name=chatbot["name"],
                maintained_by=chatbot["maintained_by"],
                is_available=chatbot["is_available"],
                last_updated=chatbot["last_updated"]
            )
            db.session.add(chatbot_instance)
        db.session.commit()

        for article in chatbot_article_data:
            chatbot_article = ChatbotArticle(
                chatbot_id=article["chatbot_id"],
                coach_id=article["coach_id"],
                title=article["title"],
                content=article["content"],
                published_at=datetime.utcnow()
            )
            db.session.add(chatbot_article)
        db.session.commit()
        print(f"Created {len(chatbot_data)} chatbot(s) and {len(chatbot_article_data)} article(s).")
    except Exception as e:
        with open("error_initial_data.txt", "w") as file:
            file.write(f"ERROR: {e}\n")
        print(f"ERROR: {e}")
        sys.exit("Exiting the program due to an exception.\n{e}")

    # HealthMetric data
    health_metrics_data = [
        {"name": "Blood Pressure", "unit": "mmHg"},
        {"name": "Blood Sugar", "unit": "mg/dL"},
        {"name": "Weight", "unit": "kg"},
        {"name": "Height", "unit": "cm"},
    ]

    try:
        for health_metric_data in health_metrics_data:
            health_metric = HealthMetric(
                coach_id=2,  # Assuming coach ID is 2
                name=health_metric_data["name"],
                unit=health_metric_data["unit"]
            )
            db.session.add(health_metric)
        db.session.commit()
        print(f"Created {len(health_metrics_data)} health metrics.")
    except Exception as e:
        with open("error_initial_data.txt", "w") as file:
            file.write(f"ERROR: {e}\n")
        print(f"ERROR: {e}")
        sys.exit("Exiting the program due to an exception.\n{e}")

    # Notifications data
    notifications_data = [
        {"title": "New Health Seminar", "message": "Join us for a new seminar on health management."},
        {"title": "Wellness Tips", "message": "Check out new wellness tips from our experts."},
    ]
    
    try:
        for notification_data in notifications_data:
            notification = Notification(
                title=notification_data["title"],
                message=notification_data["message"]
            )
            db.session.add(notification)
        db.session.commit()
        print(f"Created {len(notifications_data)} notifications.")
    except Exception as e:
        with open("error_initial_data.txt", "w") as file:
            file.write(f"ERROR: {e}\n")
        print(f"ERROR: {e}")
        sys.exit("Exiting the program due to an exception.\n{e}")


    try:
        # Fetch all users and assume some are coaches
        users = User.query.all()
        coaches = [user for user in users if 'coach' in [role.name for role in user.roles]]

        if not users or not coaches:
            print("No users or coaches available. Ensure database has users with assigned roles.")
        else:
            dummy_entries = []
            
            for user in users:
                assigned_coach = random.choice(coaches)  # Assign a random coach
                health_data = {
                    "weight": round(random.uniform(50, 100), 2),
                    "bmi": round(random.uniform(18.5, 30), 2),
                    "body_fat_percentage": round(random.uniform(10, 25), 2),
                    "steps": random.randint(3000, 15000),
                    "calories_burned": random.randint(1000, 3000)
                }
                
                entry = HealthTracker(
                    user_id=user.id,
                    coach_id=assigned_coach.id,
                    recorded_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    health_data=health_data
                )
                dummy_entries.append(entry)
            
            db.session.bulk_save_objects(dummy_entries)
            db.session.commit()
            print(f"Inserted {len(dummy_entries)} dummy health tracker records.")

    except Exception as e:
        db.session.rollback()
        print(f"Error inserting dummy health tracker records: {e}")
        sys.exit("Exiting the program due to an exception at HealthTracker.\n{e}")    