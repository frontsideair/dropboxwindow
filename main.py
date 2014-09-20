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
SECRET_KEY = '1234asjfiensjand'
DEBUG = True

window = Flask(__name__)
window.config.from_object(__name__)
sessions = {}


def flow():
    redir_url = url_for('redir', _external=True, _scheme='https')
    return DropboxOAuth2Flow(APP_KEY, APP_SECRET, redir_url, session, 'csrf')


def gen_session_name(size):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for _ in range(size))


def expired():
    time_passed = datetime.now() - session.get('created')
    return time_passed.seconds > 1800


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
    sessions[name] = session
    # maybe redirect to /<session_name>
    url = url_for('genkey', _external=True, session_name=name, _scheme='https')
    # j.mp shorten url http://dev.bitly.com/links.html#v3_shorten
    qrcode = pyqrcode.create(url, error='Q', version=5, mode='binary').text()
    return render_template('index.html', qrcode=qrcode, url=url)


@window.route('/auth/<session_name>')
def genkey(session_name):
    session = sessions.get(session_name)
    auth_url = flow().start()
    return render_template('auth.html', auth_url=auth_url)


@window.route('/redir')
def redir():
    # TODO: session open check abort(403)
    window.logger.debug(session.get('name'))
    try:
        access_token, _, _ = flow().finish(request.args)
        session['access_token'] = access_token
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
    if 'access_token' in session:
        return jsonify(authorized='true')
    else:
        return jsonify(authorized='false')


@window.route('/get/token')
def gettoken():
    return jsonify(token=session.get('access_token'))

@window.route('/logout')
def logout():
    if ('access_token' in session):
        DropboxClient(session.get('access_token')).disable_access_token()
    session.pop('session_name', None)
    return redirect(url_for('index'))  # redirect to thanks

if __name__ == '__main__':
    window.run(host='0.0.0.0')
