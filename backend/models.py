from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from sqlalchemy import func
from datetime import datetime

db = SQLAlchemy()

# --- User & Roles ---
class RolesUsers(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String)
    phone = db.Column(db.String(15))
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)

    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return f'<User {self.username}>'


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)  
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f"<Role {self.name}>"


# --- Membership ---
class Membership(db.Model):
    __tablename__ = "membership"
    id = db.Column(db.Integer, primary_key=True)
    tier = db.Column(db.String(50), nullable=False)
    requirement = db.Column(db.String(255))
    duration_months = db.Column(db.Integer, default=1)
    features = db.Column(db.Text)

    def __str__(self):
        return self.tier


# --- Events ---
class Event(db.Model):
    __tablename__ = "event"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by_user = db.relationship("User", backref="created_events")

    def __str__(self):
        return self.name


# --- Chatbot & Articles ---
class Chatbot(db.Model):
    __tablename__ = "chatbot"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), default="HealthBot")
    maintained_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_available = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return self.name


class ChatbotArticle(db.Model):
    __tablename__ = "chatbot_article"
    id = db.Column(db.Integer, primary_key=True)
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chatbot.id'))
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        return self.title


# --- Health Metrics & Tracking ---
class HealthMetric(db.Model):
    __tablename__ = "health_metric"
    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String(255), unique=True, nullable=False)  
    unit = db.Column(db.String(50), nullable=True)  

    def __str__(self):
        return f"{self.name} ({self.unit})"


class HealthTracker(db.Model):
    __tablename__ = "health_tracker"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    coach_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    health_data = db.Column(db.JSON)  # Stores key-value health data dynamically

    def __str__(self):
        return f"Health Data of {self.user_id} ({self.recorded_at})"


# --- Dashboard ---
class Dashboard(db.Model):
    __tablename__ = "dashboard"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    latest_health_status = db.Column(db.Integer, db.ForeignKey("health_tracker.id"), nullable=True)
    upcoming_events = db.relationship("Event", secondary="dashboard_events")

    def __str__(self):
        return f"{self.user_id}'s Dashboard"


class DashboardEvents(db.Model):
    __tablename__ = "dashboard_events"
    id = db.Column(db.Integer, primary_key=True)
    dashboard_id = db.Column(db.Integer, db.ForeignKey("dashboard.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))


# --- Notifications ---
class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_for = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f'<Notification(title={self.title}, created_at={self.created_at})>'


class NotificationUser(db.Model):
    __tablename__ = "notification_user"
    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.Integer, db.ForeignKey("notification.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# --- System Logs ---
class SystemLog(db.Model):
    __tablename__ = "system_log"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
