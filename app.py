import requests
from flask import Flask, render_template, jsonify, request, url_for, sessions, session, redirect
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, LoginManager, current_user, logout_user
from flask_wtf import FlaskForm
from huggingface_hub import login
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from emotion_fetcher import feelingsFetcher
from mongoModel import client, collection, chatDB, object_id

#config
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#user class
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

#register form
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


#home page
@app.route('/')
def home():
   return render_template('home.html')


#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


#register page
@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/dashboard/<username>', methods=['GET', 'POST'])
@login_required
def dashboard(username):
    return render_template('dashboard.html', username = username)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


#chatroom
@app.route('/chat/<username>/<chat_id>', methods = ['GET', 'POST'])
@login_required
def chat(chat_id, username):
    document = collection.find_one({"_id": object_id})
    average = 0

    chatrooms = document.get("chatrooms", {})
    if chat_id not in chatrooms:
        new_chatroom = {chat_id: []}

        # Update the document with the new chatroom
        collection.update_one(
            {"_id": object_id},
            {"$set": {f"chatrooms.{chat_id}": new_chatroom[chat_id]}}
        )
    return render_template('chat.html', username = username, chat_id=chat_id, status = feelingsFetcher(chat_id))


@socketio.on('message')
def handleMessage(data):
    chat_id = data['chat_id']
    username = data['username']
    message = data['message']

    collection.update_one(
        {'_id': object_id},
        {'$push': {f"chatrooms.{chat_id}": f'{username} : {message}'}}
    )
    send(f'{username}: {message}', broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)