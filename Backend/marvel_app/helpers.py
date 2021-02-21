from functools import wraps
from flask import request, jsonify
from marvel_app.models import User, Hero
from marvel_app import app
import jwt
import json
from datetime import datetime

def get_jwt(current_user):
    jwt_token = jwt.encode(
    {
        'owner':current_user.token,
        'access_time': json.dumps(datetime.utcnow(), indent=4, sort_keys=4, default=str)
    },
    app.config['SECRET_KEY'],
    algorithm = 'HS256'
    )
    return jwt_token

    

def token_required(flask_func):
    @wraps(flask_func)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing'}),401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms = ['HS256'])
            current_user_token = User.query.filter_by(token = data['owner']).first()
        except:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms = ['HS256'])
            owner = User.query.filter_by(token = data['owner']).first()
            if data['owner'] != owner.token:
                return jsonify({'message':'Your token is invalid'})
        return flask_func(current_user_token,*args,**kwargs)
    return decorated

def verify_owner(current_user_token):
    owner = Hero.query.filter_by(user_id = current_user_token.token).first()
    if owner == None:
        return jsonify({'message':'You do not have any Heroes!'})
    if owner.user_id != current_user_token.token:
        return jsonify({'message':'That token is invalid. You are not authorized'})
    return owner, current_user_token