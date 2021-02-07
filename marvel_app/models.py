from marvel_app import app, db, login_manager, ma
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
import secrets
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.queury.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.String,primary_key = True)
    first_name = db.Column(db.String(150), nullable = True, default = "")
    last_name = db.Column(db.String(150), nullable = True, default = "")
    email_address = db.Column(db.String(15), nullable = False)
    password = db.Column(db.String, nullable = True, default="")
    g_auth_verify = db.Column(db.Boolean, default = False)
    token = db.Column(db.String, unique = True)
    first_login = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    hero = db.relationship('Hero', backref = 'owner', lazy=True)

    def __init__(self, first_name = "", last_name = "", email_address = '"', password = "", g_auth_verify = False, token = ""):
        self.id = self.set_id()
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.password = self.set_password(password)
        self.g_auth_verify = g_auth_verify
        self.token = self.set_token(24)

    def set_token(self, length):
        return secrets.token_hex(length)

    def set_id(self):
        return str(uuid.uuid4())

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
        return self.pw_hash

class Hero(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    hero_name = db.Column(db.String(150), nullable = True, default = "")
    description = db.Column(db.String(300), nullable = True, default = "")
    comics_appeared = db.Column(db.Integer, nullable = True)
    super_power = db.Column(db.String(200), nullable = True, default = "")
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    owner = db.Column(db.String, db.ForeignKey('user.token'), nullable = False)

    def __init__(self, id, hero_name = "",description = "",comics_appeared = 0,super_power = "", owner=""):
        self.id = id
        self.hero_name = hero_name
        self.description = description
        self.comics_appeared = comics_appeared
        self.super_power = super_power
        self.owner = owner

class HeroSchema(ma.Schema):
    class Meta:
        fields = ('id','hero_name','description','comics_appeared','super_power')

hero_schema = HeroSchema
heroes_schema = HeroSchema(many = True)