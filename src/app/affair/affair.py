from flask import Blueprint
from flask import render_template, request, redirect

from flask_login import login_required, current_user
from .mail import send_file

affairs = Blueprint('affairs', __name__, template_folder='templates')


@affairs.route('/affair')
@login_required
def affair():
    return render_template('affair/affair.html')

@affairs.route('/fetch', methods=['POST'])
@login_required
def fetch():
    email = current_user.email
    # send_file(email, )
    return render_template('affair/fetch.html')
