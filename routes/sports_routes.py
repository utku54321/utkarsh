import os
import requests
from flask import Blueprint, render_template, jsonify

bp = Blueprint('sports', __name__)

API_KEY = os.getenv('API_FOOTBALL_KEY')
API_HOST = os.getenv('API_FOOTBALL_HOST', 'v3.football.api-sports.io')


@bp.route('/', methods=['GET'])
def view():
    return render_template('sports.html')


@bp.route('/live', methods=['GET'])
def live():
    if not API_KEY:
        return jsonify({'ok': False, 'error': 'Set API_FOOTBALL_KEY in .env'}), 400
    url = f"https://{API_HOST}/fixtures?live=all"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
    response = requests.get(url, headers=headers, timeout=20)
    try:
        return jsonify({'ok': True, 'data': response.json()})
    except Exception:
        return jsonify({'ok': False, 'status': response.status_code, 'text': response.text[:500]}), 502
