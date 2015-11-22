#
# file: project.py
# author: lyn.evans
# date: 09.07.15
#
import cgi
import sys
import random
import string
import httplib2
import json
import requests
import datetime
from urlparse import urljoin
from flask import Flask, render_template, url_for, request
from flask import redirect, flash, jsonify
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Era, Composer
from sqlalchemy.orm import relationship
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from werkzeug.contrib.atom import AtomFeed

# Constant Strings
editCompUrl = "/era/<string:era_name>/<string:composer_name>/edit"
delCompUrl = "/era/<string:era_name>/<string:composer_name>/delete"
tokenExpErr = "Token expired or revoked"

# Generate unique client id
secretsFile = 'client_secrets.json'
CLIENT_ID = json.loads(open(secretsFile, 'r').read())['web']['client_id']
app = Flask(__name__)

# Initialize database ORM session
db_url = 'postgresql://vagrant:vagrant@localhost:5432/vagrant'
db_engine = create_engine(db_url)
Base.metadata.bind = db_engine
DBSession = sessionmaker(bind=db_engine)
session = DBSession()


# Url util
def make_external(url):
    return urljoin(request.url_root, url)


# Login
@app.route('/login')
def showLogin():
    rand = random.choice(string.ascii_uppercase + string.digits)
    state = ''.join(rand for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)


# 3rd party authorization via Google+
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    str_creds = login_session.get('credentials')
    str_gp_id = login_session.get('gplus_id')
    if str_creds is not None and gplus_id == str_gp_id:
        resp_str = 'Current user is already connected.'
        response = make_response(json.dump(resp_str),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    # Avoid exception - Oauth2 credentials object 'Not serializable'
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['logged_in'] = True

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    print "done!"
    return output


# Revoke user's Google+ authorization token
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    j_cred = json.loads(credentials)
    access_token = j_cred['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result, content = h.request(url, 'GET')

    try:
        r_content = json.loads(content)
    except:
        r_content = {}
        r_content['errtxt'] = ""

    if result['status'] == '200' or r_content['errtxt'] == tokenExpErr:
        # Reset the user's sesson.
        del login_session['logged_in']
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        # return response
        return redirect('/')
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Json endpoints - return composers per era
@app.route('/era/<int:era_id>/list/JSON')
def composersByEraJson(era_id):
    try:
        era = session.query(Era).filter_by(id=era_id).one()
        composers = session.query(Composer).filter_by(era=era) \
            .order_by(Composer.name).all()
        return jsonify(Composers=[c.serialize for c in composers])
    except:
        return 'Error occurred'


# Json endpoints - return full musical data set w/ eras and composers per era
@app.route('/era/list/JSON')
def eraJson():
    eras = session.query(Era).all()
    jlist = []
    for era in eras:
        composers = session.query(Composer).filter_by(era=era) \
            .order_by(Composer.name).all()
        d = {}
        clist = [c.serialize for c in composers]
        jlist.append({'id': era.id, 'name': era.name, 'Composers': clist})
    return jsonify(Musical_Eras=jlist)


# Json endpoints - return composer detail
@app.route('/era/<int:era_id>/composer/<int:composer_id>/JSON')
def composerJson(era_id, composer_id):
    try:
        era = session.query(Era).filter_by(id=era_id).one()
        composer = session.query(Composer).filter_by(id=composer_id).one()
        result = composer.serialize
        result['era_name'] = era.name
        return jsonify(Composer=result)
    except:
        return 'Error occurred'


# Atom endpoint
@app.route('/composers.atom')
def composers_feed():
    feed = AtomFeed('Classical Composers',
                    feed_url=request.url, url=request.url_root)
    composers = session.query(Composer).all()
    for comp in composers:
        feed.add(
            comp.name, unicode(comp.description),
            content_type='html',
            era=comp.era.name,
            url=make_external(
                url_for(
                    'composerDetail',
                    era_name=comp.era.name,
                    composer_name=comp.name
                )
            ),
            updated=datetime.datetime.utcnow()
        )
    return feed.get_response()


# Context root - render main musical 'eras' page
@app.route('/')
def eraList():
    rand = random.choice(string.ascii_uppercase + string.digits)
    state = ''.join(rand for x in xrange(32))
    login_session['state'] = state
    page = 'eras.html'
    eras = session.query(Era).all()
    composers = session.query(Composer).order_by(Composer.name).all()
    return render_template(page, eras=eras,
                           composers=composers, era_name="",
                           logged_in=isUserLoggedIn())


# Render composers per era page
@app.route('/era/<string:era_name>/composers')
def composersByEraList(era_name):
    try:
        era = session.query(Era).filter_by(name=era_name).one()
        all_eras = session.query(Era).all()
        filtered_composers = session.query(Composer).filter_by(era=era) \
            .order_by(Composer.name).all()
        return render_template(
            'eras.html',
            eras=all_eras,
            composers=filtered_composers,
            era_name=era.name,
            logged_in=isUserLoggedIn()
        )
    except:
        return 'Error occurred'


# Render composer detail
@app.route('/era/<string:era_name>/<string:composer_name>')
def composerDetail(era_name, composer_name):
    try:
        era = session.query(Era).filter_by(name=era_name).one()
        c_composer = session.query(Composer).filter_by(
            name=composer_name.replace("%20", " ")
        ).one()
        return render_template(
            'composer.html',
            composer=c_composer, era=era,
            logged_in=isUserLoggedIn()
        )
    except:
        return 'Error occurred'


# Process Create requests
@app.route('/era/composer/new', methods=['GET', 'POST'])
def newComposer():
    if not isUserLoggedIn():
        return redirect('/login')
    try:
        if request.method == 'POST':
            c_era = session.query(Era).filter_by(
                id=request.form['composer_era']
            ).one()
            new_composer = Composer(
                name=request.form['composer_name'],
                description=request.form['description'],
                era=c_era
            )
            session.add(new_composer)
            session.commit()
            flash("New composer added!")
            return redirect(url_for('eraList'))
        else:
            eras = session.query(Era).all()
            return render_template(
                'add_composer.html',
                eras=eras,
                logged_in=isUserLoggedIn()
            )
    except:
        return 'Error occurred'


# Process Update requests
@app.route(editCompUrl, methods=['GET', 'POST'])
def editComposer(era_name, composer_name):
    if not isUserLoggedIn():
        return redirect('/login')
    try:
        c_era = session.query(Era).filter_by(name=era_name).one()
        c_composer = session.query(Composer) \
            .filter_by(name=composer_name).one()
        eras = session.query(Era).all()
        if request.method == 'POST':
            update_era = session.query(Era).filter_by(
                id=request.form['composer_era']
            ).one()
            c_composer.name = request.form['composer_name']
            c_composer.description = request.form['description']
            c_composer.era = update_era
            session.add(c_composer)
            session.flush()
            flash("Composer %s updated!" % c_composer.name)
            return redirect(
                url_for(
                    'composerDetail',
                    era_name=c_era.name, composer_name=c_composer.name
                )
            )
        else:
            return render_template(
                'edit_composer.html',
                era=c_era, composer=c_composer, eras=eras,
                logged_in=isUserLoggedIn()
            )
    except:
        return 'Error occurred'


# Process Delete requests
@app.route(delCompUrl, methods=['GET', 'POST'])
def deleteComposer(era_name, composer_name):
    if not isUserLoggedIn():
        return redirect('/login')
    try:
        c_era = session.query(Era).filter_by(name=era_name).one()
        c_composer = session.query(Composer).filter_by(name=composer_name) \
            .one()
        if request.method == 'POST':
            composer = session.query(Composer) \
              .filter_by(name=composer_name).first()
            session.delete(composer)
            session.commit()
            flash("Composer %s deleted!" % c_composer.name)
            return redirect(url_for('composersByEraList', era_name=era_name))
        else:
            return render_template(
                'delete_composer.html',
                era=c_era,
                composer=c_composer,
                logged_in=isUserLoggedIn()
            )
    except:
        return 'Error occurred'


# Utility to check user's login status
def isUserLoggedIn():
    try:
        return login_session['logged_in']
    except:
        return False

if __name__ == '__main__':
    rand = random.choice(string.ascii_uppercase + string.digits)
    skey = ''.join(rand for x in xrange(32))

    app.secret_key = skey
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
