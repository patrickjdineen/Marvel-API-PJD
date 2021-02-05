from marvel_api import app, db, login_manager
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
import secrets
from flask_login import UserMixin

@login_manger.user_loader
def load_user(user_id):
    return User.queury.get(user_id)

Def User(db.Model, UserMixin)