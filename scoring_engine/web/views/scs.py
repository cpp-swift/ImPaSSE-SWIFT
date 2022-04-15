from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user
from scoring_engine.models.scs import SCS
from scoring_engine.models.setting import Setting
from scoring_engine.db import session


mod = Blueprint('scs', __name__)


@mod.route('/scs')
@login_required
def home():
    if not current_user.is_blue_team:
        return redirect(url_for('auth.unauthorized'))
    return render_template('scs.html', team_name=current_user.team.name, team_id=current_user.team.id)

@mod.route('/scs/<id>')
@login_required
def scs(id):
    scs = session.query(SCS).get(id)
    if scs is None or not current_user.team == scs.team:
        return redirect(url_for('auth.unauthorized'))
    modify_account_usernames_setting = Setting.get_setting('blue_team_update_account_usernames').value
    modify_account_passwords_setting = Setting.get_setting('blue_team_update_account_passwords').value

    return render_template(
        'scs.html',
        id=id,
        scs=scs,
        modify_hostname_setting=modify_hostname_setting,
        modify_port_setting=modify_port_setting,
        modify_account_passwords_setting=modify_account_passwords_setting,
        modify_account_usernames_setting=modify_account_usernames_setting
    )
