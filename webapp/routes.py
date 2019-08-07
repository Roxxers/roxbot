
from quart import session, redirect, request, url_for, jsonify, render_template, abort
import webapp
from webapp import oauth, app, config
import discord


def requires_login(func):
    def wrapper(*args, **kwargs):
        if session.get('oauth2_token', None) is None:
            session['login_referrer'] = url_for(func.__name__)
            return redirect(url_for("login"))
        else:
            return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # Weird work around needed to decorate app routes
    return wrapper


@app.route("/")
async def index():
    oauth_token = session.get('oauth2_token', None)
    if oauth_token:
        discord_session = oauth.make_session(token=oauth_token)
        logged_in_user = discord_session.get(app.config["API_BASE_URL"] + '/users/@me').json()
    else:
        discord_session = {}
        logged_in_user = {}

    return await render_template(
        "index.html",
        oauth_token=oauth_token,
        discord_session=discord_session,
        logged_in_user=logged_in_user,
        IMAGE_BASE_URL=app.config["IMAGE_BASE_URL"],
        client=app.discord_client,
        invite_url=discord.utils.oauth_url(app.discord_client.user.id, permissions=discord.Permissions(1983245558), redirect_uri=url_for("index", _external=True))
    )


@app.route('/about')
async def about():
    return ""


@app.route('/docs')
async def docs():
    return redirect("https://roxxers.github.io/roxbot/")


@app.route("/settings/instance")
@requires_login
async def instance():
    oauth_token = session.get('oauth2_token')
    if oauth_token is None:
        return redirect(url_for("login"))

    if app.config["INSTANCE_OWNER_ID"] != session['user']['id']:
        abort(401)

    return await render_template("settings/settings.html", bot=webapp._discord.bot.client.user)


@app.route('/dashboard')
@requires_login
async def dashboard():
    roxbot_guilds = app.discord_client.guilds
    def filter_guilds(guild):
        g_ids = [str(x.id) for x in roxbot_guilds]
        if guild.get('id', 0) in g_ids:
            return True
        else:
            return False

    oauth_token = session.get('oauth2_token')
    discord_session = oauth.make_session(token=oauth_token)
    guilds = discord_session.get(app.config["API_BASE_URL"] + '/users/@me/guilds').json()
    guilds = list(filter(filter_guilds, guilds))
    user = discord_session.get(app.config["API_BASE_URL"] + '/users/@me').json()

    return await render_template(
        "dashboard.html",
        oauth_token=oauth_token,
        user=user,
        guilds=sorted(guilds, key=lambda k: k['name']),
        IMAGE_BASE_URL=app.config["IMAGE_BASE_URL"]
    )


@app.route('/guilds/<guild_id>')
@requires_login
async def guild_page(guild_id):
    oauth_token = session.get('oauth2_token')
    if oauth_token is None:
        return redirect(url_for("login"))

    discord_session = oauth.make_session(token=oauth_token)
    guilds = discord_session.get(app.config["API_BASE_URL"] + '/users/@me/guilds').json()
    guild = list(filter(lambda a: a != -1, [x if guild_id == x['id'] else -1 for x in guilds]))

    return jsonify(guild)


@app.route('/me')
@requires_login
async def me():
    if session.get('oauth2_token') is None:
        return redirect(url_for("login"))

    oauth_token = session.get('oauth2_token', None)
    discord_session = oauth.make_session(token=oauth_token)
    return jsonify(discord_session.get(app.config["API_BASE_URL"] + '/users/@me').json())


###########
#  OAUTH  #
###########


@app.route('/login')
async def login():
    scope = request.args.get(
        'scope',
        'identify guilds')
    discord = oauth.make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(app.config["AUTHORIZATION_BASE_URL"])
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route('/logout')
async def logout():
    session.clear()
    return redirect(url_for(".index"))


@app.route('/callback')
async def callback():
    form = await request.form
    if form.get('error'):
        return form['error']
    discord_session = oauth.make_session(state=session.get('oauth2_state'))

    token = discord_session.fetch_token(
        app.config["TOKEN_URL"],
        client_secret=app.config["OAUTH2_CLIENT_SECRET"],
        authorization_response=request.url)
    session['oauth2_token'] = token
    session['user'] = discord_session.get(app.config["API_BASE_URL"] + '/users/@me').json()
    return redirect(session['login_referrer'])





