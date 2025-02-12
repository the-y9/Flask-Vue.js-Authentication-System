from flask_restful import Resource, Api, reqparse, marshal_with, fields
from flask_security import auth_required, roles_required, current_user
from sqlalchemy import func
from flask import jsonify, request
from .models import db, User, HealthTracker
import requests
from datetime import datetime
import pandas as pd
import json
import re

api = Api()

class HealthTrackerRCS(Resource):
    # @auth_required("token")
    def get(self, user_id):
        if user_id:
            try:
                health_tracker = HealthTracker.query.filter_by(user_id=user_id).order_by(HealthTracker.recorded_at.asc()).all()
                if not health_tracker:
                    return jsonify({"message": "No health data found for the user."})
                return jsonify({"data": [health.serialize() for health in health_tracker]})
            except Exception as e:
                return jsonify({"message": f"Error: {e}"})
        return jsonify({"message": "User ID is required."})

api.add_resource(HealthTrackerRCS, "/health-tracker/<int:user_id>")
