from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, redirect, url_for, request, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import SignUpForm, TaskForm, LoginForm
from models import db, User, Task
from datetime import datetime
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
migrate = Migrate(app, db)


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            form.username.errors.append('Username already exists. Please choose another username.')
        elif existing_email:
            form.email.errors.append('This email is already registered. Please use another email.')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            # print(f"User password before commit: {new_user.password_hash}")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('tasks'))
        flash('Login unsuccessful. Please check your email and password.')
    
    return render_template('login.html', form=form)


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    task_form = TaskForm()
    if request.method == 'POST':
        content = request.form['content']
        new_task = Task(content=content, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('tasks'))
    
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', user_tasks=user_tasks, task_form=task_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)




