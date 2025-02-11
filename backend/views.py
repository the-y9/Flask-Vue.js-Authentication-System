from flask import current_app as app, jsonify,request, render_template, send_file
from flask_security import auth_required, roles_required
from werkzeug.security import check_password_hash,generate_password_hash
from backend.security import datastore 
from flask_restful import marshal, fields
import flask_excel as excel
from .models import User, db
from sqlalchemy import or_ 
import smtplib

@app.get('/')
def home():
    return render_template('index.html')

@app.get('/root')
@auth_required("token")
@roles_required("root")
def root():
    return "Welcome root"

@app.post('/user-signup')
def signup():
    data = request.get_json()
    if datastore.find_user(email=data.get('email')):
        return jsonify({'message': 'Email already registered'}), 409
    if datastore.find_user(username=data.get('username')):
        return jsonify({'message': 'Username already registered'}), 409
    if not data.get("password"):
        return jsonify({"message":"Password not provided"}), 400
       
    try:
        datastore.create_user(
            email=data['email'],
            username=data['username'],
            password=generate_password_hash(data['password']),
            roles=['member'],  
            active=True
        )
        db.session.commit()
        return jsonify({'message': 'Successfully registered as member.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error occurred while creating the user account - ' + str(e)}), 500
    


@app.post('/user-login')
def user_login():
    data = request.get_json()
    username = data.get('username')

    print(username)
    if not username:
        return jsonify({"message":"Username not provided"}),400
    if not data.get("password"):
        return jsonify({"message":"Password not provided"}),400
    
    if '@' in username:
        user = datastore.find_user(email=username)
        
    else:
        user = datastore.find_user(username=username)
    
    if not user:
        return jsonify({"message":"Username not found."}),404
    
    if check_password_hash(user.password, data.get("password")):
        if user.active:
            return jsonify({"token":user.get_auth_token(),"id":user.id,"username":user.username,"role":user.roles[0].name}),200
        else:
            return jsonify({"message":"User not activated"}),401
    
    else: 
        return jsonify({"message":"Wrong password"}),401


# @app.post('/upload')
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file uploaded'})

#     file = request.files['file']
#     milestone_id = request.form.get('milestoneId')

#     if not file:
#         return jsonify({'error': 'File is required'})
#     try:
#         file.save(f'uploads/{milestone_id}_{file.filename}')
#         return jsonify({'message': 'File uploaded successfully'})
#     except Exception as e:
#         return jsonify({'error': str(e)})

    
