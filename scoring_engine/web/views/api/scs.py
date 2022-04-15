from flask import request, jsonify
from flask_login import current_user, login_required

import html

from scoring_engine.cache import cache
from scoring_engine.db import session
from scoring_engine.cache_helper import (
    update_overview_data,
)
from scoring_engine.models.account import Account
from scoring_engine.models.scs import SCS
from scoring_engine.models.setting import Setting
from scoring_engine.models.check import Check
from scoring_engine.models.round import Round

from . import mod


@mod.route("/api/scs/<scs_id>/checks")
@login_required
@cache.memoize()
def scs_get_checks(scs_id):
    scs = session.query(SCS).get(scs_id)
    if scs is None or not (
        current_user.team == scs.team or current_user.team.is_white_team
    ):
        return jsonify({"status": "Unauthorized"}), 403
    data = []
    check_output = (
        session.query(Check, Round.number)
        .join(Round)
        .filter(Check.scs_id == scs_id)
        .order_by(Check.id.desc())
        .all()
    )
    data = [
        {
            "id": check[0].id,
            "round": check[1],
            "result": check[0].result,
            "timestamp": check[0].local_completed_timestamp,
            "reason": check[0].reason,
            "output": check[0].output,
            "command": check[0].command,
        }
        for check in check_output
    ]
    if (
        Setting.get_setting("blue_team_view_check_output").value is False
        and current_user.is_blue_team
    ):
        for check in data:
            check["output"] = "REDACTED"
    return jsonify(data=data)


@mod.route("/api/scs/update_account", methods=["POST"])
@login_required
def update_scs_account_info():
    if current_user.is_white_team or current_user.is_blue_team:
        if "name" in request.form and "value" in request.form and "pk" in request.form:
            account = session.query(Account).get(int(request.form["pk"]))
            if current_user.team == account.scs.team or current_user.is_white_team:
                if account:
                    if request.form["name"] == "username":
                        modify_usernames_setting = Setting.get_setting(
                            "blue_team_update_account_usernames"
                        )
                        if modify_usernames_setting.value is True or current_user.is_white_team:
                            account.username = html.escape(request.form["value"])
                    elif request.form["name"] == "password":
                        modify_password_setting = Setting.get_setting(
                            "blue_team_update_account_passwords"
                        )
                        if modify_password_setting.value is True or current_user.is_white_team:
                            account.password = html.escape(request.form["value"])
                    session.add(account)
                    session.commit()
                    return jsonify({"status": "Updated Account Information"})
                return jsonify({"error": "Incorrect permissions"})
            return jsonify({"error": "Incorrect permissions"})
    return jsonify({"error": "Incorrect permissions"})

