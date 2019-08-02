
from quart import session, redirect, request, url_for, jsonify, render_template
import webapp
from webapp import oauth, app


@app.route("/")
async def index():
    oauth_token = session.get('oauth2_token', None)
    if oauth_token:
        discord_session = oauth.make_session(token=oauth_token)
        user = discord_session.get(webapp.API_BASE_URL + '/users/@me').json()
    else:
        discord_session = {}
        user = {}

    return await render_template(
        "index.html",
        oauth_token=oauth_token,
        discord_session=discord_session,
        user=user,
        IMAGE_BASE_URL=webapp.IMAGE_BASE_URL
    )

@app.route('/stats')
async def stats():
    return ""


@app.route('/guilds')
async def guilds():
    oauth_token = session.get('oauth2_token')
    if oauth_token is None:
        return redirect(url_for("login"))

    discord_session = oauth.make_session(token=oauth_token)
    guilds = discord_session.get(webapp.API_BASE_URL + '/users/@me/guilds').json()
    user = discord_session.get(webapp.API_BASE_URL + '/users/@me').json()

    return await render_template(
        "guilds.html",
        oauth_token=oauth_token,
        user=user,
        guilds=sorted(guilds, key=lambda k: k['name']),
        IMAGE_BASE_URL=webapp.IMAGE_BASE_URL
    )


@app.route('/guilds/<guild_id>')
async def guild_page(guild_id):
    oauth_token = session.get('oauth2_token')
    if oauth_token is None:
        return redirect(url_for("login"))

    discord_session = oauth.make_session(token=oauth_token)
    guilds = discord_session.get(webapp.API_BASE_URL + '/users/@me/guilds').json()
    guild = list(filter(lambda a: a != -1, [x if guild_id == x['id'] else -1 for x in guilds]))

    return jsonify(guild)


@app.route('/me')
async def me():
    if session.get('oauth2_token') is None:
        return redirect(url_for("login"))

    oauth_token = session.get('oauth2_token', None)
    discord_session = oauth.make_session(token=oauth_token)
    return jsonify(discord_session.get(webapp.API_BASE_URL + '/users/@me').json())


###########
#  OAUTH  #
###########

@app.route('/login')
async def login():
    scope = request.args.get(
        'scope',
        'identify guilds')
    discord = oauth.make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(webapp.AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route('/logout')
async def logout():
    await session.clear()
    return redirect(url_for(".index"))


@app.route('/callback')
async def callback():
    form =  await request.form
    if form.get('error'):
        return form['error']
    discord = oauth.make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        webapp.TOKEN_URL,
        client_secret=webapp.OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token
    return redirect(url_for('index'))





