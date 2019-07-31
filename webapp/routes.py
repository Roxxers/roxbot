
from flask import session, redirect, request, url_for, jsonify, render_template
import webapp
from webapp import oauth, app


@app.route("/")
def index():
    oauth_token = session.get('oauth2_token', None)
    if oauth_token:
        discord_session = oauth.make_session(token=oauth_token)
        user = discord_session.get(webapp.API_BASE_URL + '/users/@me').json()
    else:
        discord_session = {}
        user = {}

    print(user)
    return render_template(
        "index.html",
        oauth_token=oauth_token,
        discord_session=discord_session,
        user=user,
        IMAGE_BASE_URL=webapp.IMAGE_BASE_URL
    )


@app.route('/login')
def login():
    scope = request.args.get(
        'scope',
        'identify guilds')
    discord = oauth.make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(webapp.AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for(".index"))


@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = oauth.make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        webapp.TOKEN_URL,
        client_secret=webapp.OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token
    return redirect(url_for('index'))


@app.route('/me')
def me():
    if session.get('oauth2_token') is None:
        return redirect(url_for("index"))

    oauth_token = session.get('oauth2_token', None)

    discord_session = oauth.make_session(token=oauth_token)


    return jsonify(discord_session.get(webapp.API_BASE_URL + '/users/@me').json())
