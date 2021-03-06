import json

from collections import OrderedDict

from flask import jsonify
from flask_login import current_user, login_required

from scoring_engine.cache import cache
from scoring_engine.db import session
from scoring_engine.models.team import Team

from . import mod


@mod.route('/api/team/<team_id>/stats')
@login_required
@cache.memoize()
def services_get_team_data(team_id):
    team = session.query(Team).get(team_id)
    if team is None or not current_user.team == team or not current_user.is_blue_team:
        return {'status': 'Unauthorized'}, 403

    data = {
        'place': team.place,
        'current_score': team.current_score,
    }
    return jsonify(data)


@mod.route('/api/team/<team_id>/scs')
@login_required
@cache.memoize()
def api_scs(team_id):
    team = session.query(Team).get(team_id)
    if team is None or not current_user.team == team or not current_user.is_blue_team:
        return {'status': 'Unauthorized'}, 403
    data = []
    sorted_scs = sorted(team.scs, key=lambda scs: scs.id)
    for scs in sorted_scs:
        if scs.last_check_result():
            data.append(dict(
                hostname=scs.hostname,
                configuration_text=scs.configuration_text
            ))
    return jsonify(data=data)

@mod.route('/api/team/<team_id>/services')
@login_required
@cache.memoize()
def api_services(team_id):
    team = session.query(Team).get(team_id)
    if team is None or not current_user.team == team or not current_user.is_blue_team:
        return {'status': 'Unauthorized'}, 403
    data = []
    sorted_services = sorted(team.services, key=lambda service: service.id)
    for service in sorted_services:
        if not service.checks:
            check = 'Undetermined'
        else:
            if service.last_check_result():
                check = 'UP'
            else:
                check = 'DOWN'
        data.append(dict(
            service_id=service.id,
            service_name=service.name,
            host=service.host,
            port=service.port,
            check=check,
            rank=service.rank,
            score_earned=service.score_earned,
            max_score=service.max_score,
            percent_earned=service.percent_earned,
            pts_per_check=service.points,
            last_ten_checks=[check.result for check in service.last_ten_checks[::-1]]
        ))
    return jsonify(data=data)


@mod.route('/api/team/<id>/services/status')
@login_required
@cache.memoize()
def team_services_status(id):
    if current_user.is_blue_team and current_user.team.id == int(id):
        services = OrderedDict()
        team = session.query(Team).get(id)
        sorted_services = sorted(team.services, key=lambda service: service.id)
        for service in sorted_services:
            services[service.name] = {
                'id': str(service.id),
                'result': str(service.last_check_result()),
            }
        return json.dumps(services)
    return jsonify({'status': 'Unauthorized'}), 403
