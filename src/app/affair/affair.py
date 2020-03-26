import os
from datetime import datetime

from flask import Blueprint
from flask import render_template, request, redirect

from flask_login import login_required, current_user
from .mail import send_file
from .export import export
from ..defines import names

affairs = Blueprint('affairs', __name__, template_folder='templates')


@affairs.route('/affair')
@login_required
def affair():    
    return render_template('affair/affair.html', year=datetime.today().year)

@affairs.route('/fetch', methods=['POST'])
@login_required
def fetch():
    years = request.form.getlist('year')
    email = current_user.email
    filename = export(years)
    send_file(email, names[email], filename)
    return render_template('affair/fetch.html')
