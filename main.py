from flask import (Flask, render_template, redirect, request, session, url_for,
                   jsonify)
from dropbox.client import DropboxOAuth2Flow, DropboxClient
from datetime import datetime
import os
import pyqrcode
import random

APP_KEY = os.environ.get('APP_KEY')
APP_SECRET = os.environ.get('APP_SECRET')
window = Flask(__name__)
window.secret_key = '1234asjfiensjand'
window.debug = True


def flow(session_name):
    redir_url = url_for('redirect', session_name=session_name, _external=True)
    redir_url = redir_url.replace('http', 'https')  # dirty hack
    this_session = session[session_name]
    return DropboxOAuth2Flow(APP_KEY, APP_SECRET, redir_url, this_session,
                             'csrf-token')


def gen_session_name(size):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for _ in range(size))


def expired(session_name):
    time_passed = datetime.now() - session[session_name]['expires']
    return time_passed.seconds > 1800


@window.route('/')
def index():
    session_name = gen_session_name(8)
    session[session_name] = {'expires': datetime.now()}
    url = url_for('genkey', _external=True, session_name=session_name)
    window.logger.debug(url)
    qrcode = pyqrcode.create(url, error='Q', version=4).text()
    qrcode = qrcode.replace('0', u'\u25a1').replace('1', u'\u25a0')
    return render_template('index.html', qrcode=qrcode, url=url)


@window.route('/auth/<session_name>')
def genkey(session_name):
    if session_name in session and not expired(session_name):
        auth_url = flow(session_name).start()
        return render_template('auth.html', auth_url=auth_url)
    else:
        session.pop(session_name)
        return render_template('error.html', error='Session not found')


@window.route('/redir/<session_name>', methods=['GET'])
def redirect(session_name):
    try:
        access_token, _, _ = flow(session_name).finish(request.query_params)
        session[session_name]['access_token'] = access_token
        return render_template('success.html')
    except:
        return render_template('error.html', error='Auth unsuccessful')


@window.route('/get/<session_name>')
def keyget(session_name):
    if session_name in session and 'access_token' in session[session_name]:
        return jsonify(access_token=session[session_name]['access_token'])
    else:
        return jsonify(access_token='null')


@window.route('/exit/<session_name>')
def exit(session_name):
    session.pop(session_name)

if __name__ == '__main__':
    window.run(host='0.0.0.0')
