from flask import (Flask, render_template, redirect, request, session, url_for,
                   jsonify, send_from_directory)
from dropbox.client import DropboxOAuth2Flow, DropboxClient
from datetime import datetime
import os
import pyqrcode
import random

APP_KEY = os.environ.get('APP_KEY')
APP_SECRET = os.environ.get('APP_SECRET')
HEROKU = os.environ.get('HEROKU')
SECRET_KEY = os.environ.get('FLASK_SECRET')
DEBUG = True
scheme = 'https' if HEROKU == 'true' else 'http'

window = Flask(__name__)
window.config.from_object(__name__)
auth_tokens = {}


def flow():
    redir_url = url_for('redir', _external=True, _scheme=scheme)
    return DropboxOAuth2Flow(APP_KEY, APP_SECRET, redir_url, session, 'csrf')


def gen_session_name(size):
    # TODO: generate 4-word name from dict
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for _ in range(size))


def expired():
    time_passed = datetime.now() - session.get('created')
    return time_passed.seconds > 1800


def purge_sessions():
    # TODO: purge sessions older than 30 mins
    pass


@window.route('/robots.txt')
@window.route('/humans.txt')
@window.route('/qrcode.ttf')
@window.route('/manifest.webapp')
def serve_static_content():
    return send_from_directory(window.static_folder, request.path[1:])


@window.route('/')
def index():
    name = gen_session_name(8)
    session['name'] = name
    session['created'] = datetime.now()
    # redirect to /<session_name>
    url = url_for('genkey', _external=True, session_name=name, _scheme=scheme)
    qrcode = pyqrcode.create(url, error='Q', version=4, mode='binary').text()
    return render_template('index.html', qrcode=qrcode, url=url)


@window.route('/auth/<session_name>')
def genkey(session_name):
    session['name'] = session_name
    auth_url = flow().start()
    return render_template('auth.html', auth_url=auth_url)


@window.route('/redir')
def redir():
    # TODO: session open check abort(403)
    try:
        access_token, _, _ = flow().finish(request.args)
        auth_tokens[session['name']] = access_token
        return render_template('success.html')
    except DropboxOAuth2Flow.BadRequestException, e:
        window.logger.exception(e)
        return render_template('error.html', error=e)
    except DropboxOAuth2Flow.BadStateException, e:
        window.logger.exception(e)
        return render_template('error.html', error=e)
    except DropboxOAuth2Flow.CsrfException, e:
        window.logger.exception(e)
        return render_template('error.html', error=e)
    except DropboxOAuth2Flow.NotApprovedException, e:
        window.logger.exception(e)
        return render_template('error.html', error=e)
    except DropboxOAuth2Flow.ProviderException, e:
        window.logger.exception(e)
        return render_template('error.html', error=e)


@window.route('/get')
def getmessage():
    if session['name'] in auth_tokens:
        return jsonify(authorized='true')
    else:
        return jsonify(authorized='false')


@window.route('/get/token')
def gettoken():
    return jsonify(token=auth_tokens.get(session['name']))


@window.route('/logout')
def logout():
    if session['name'] in auth_tokens:
        DropboxClient(auth_tokens.get(session['name'])).disable_access_token()
        auth_tokens.pop(session['name'], None)

if __name__ == '__main__':
    window.run(host='0.0.0.0')
