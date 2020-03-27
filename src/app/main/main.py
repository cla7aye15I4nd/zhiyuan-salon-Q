from flask import Blueprint
from flask import render_template, request

from flask_login import current_user

from . import update
from ..defines import *

main = Blueprint('main', __name__, template_folder='templates')

update.update_text()
main.table = update.get_map()

@main.route('/')
def index():    
    time = update.check_update_time(main)    
    return render_template('main/index.html', time=time)

@main.route('/result')
def result():
    id = request.args.get('id', type=str, default='')
    
    if id not in main.table:
        return render_template('main/result.html', error=True)
    else:
        report = main.table[id]
        report.stuid = id
        report.count_all = report.count_zy + report.count_other
        report.all_ok = report.count_all >= 16
        report.zy_ok = report.count_zy >= 12
        report.has_acts_zy = len(report.acts_zy) > 0
        report.has_acts_other = len(report.acts_other) > 0
        return render_template('main/result.html', report=report)
