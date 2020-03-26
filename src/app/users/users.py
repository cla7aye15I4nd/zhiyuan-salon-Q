from flask import Blueprint
from flask import render_template, request, redirect

from flask_login import login_required, current_user
from flask_login import login_user, logout_user, LoginManager
from flask_sqlalchemy import SQLAlchemy

from .forms import LoginForm, RegisterForm
from .models import db, Users
from ..defines import names

login_manager = LoginManager()

users = Blueprint('users', __name__, template_folder='templates')

@login_manager.user_loader
def load_user(id):
    return Users.query.filter_by(id=id).first()

@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

def login_validate():
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')

        user = Users.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return True
    return False

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'GET':
        return render_template('users/login.html')

    if request.method == 'POST':
        if login_validate():
            return redirect('/')
        else:
            return render_template('users/login.html', error=True)

def register_validate():    
    form = RegisterForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')

        if email not in names:
            return False

        result = Users.query.filter_by(email=email).first()
        if result is not None:
            return False

        user = Users(email, password)
        db.session.add(user)
        db.session.commit()
        return True
    return False

@users.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('users/register.html')
    if request.method == 'POST':
        if register_validate():
            return redirect('/login')
        else:
            return render_template('users/register.html', error=True)
