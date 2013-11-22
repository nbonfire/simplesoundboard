import pygame
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid, admin
from forms import LoginForm
from models import User, ROLE_USER, ROLE_ADMIN
from datetime import datetime
from decorators import login_required, async
from config import basedir

pygame.mixer.init()
fxchannel=pygame.mixer.Channel(1)
SONG_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END)
resume_volume()

@async
def resume_volume():
	while True:
		for event in pygame.event.get():
			if event.type == SONG_END and not pygame.mixer.music.get_busy():
				print "the song ended, resume xbmc volume"

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()

@app.route("/")
@app.route("/index")
@login_required
def index():
	tagsandsounds=[{'category':x, 'sounds':[{'file': y.filename, 'name':y.name} for y in x.sounds]} for x in db.session.query(Tag).all() ]
	return render_template('soundboard.html', filenamesandcategories=tagsandsounds, jqueryurl=url_for('static', filename='js/jquery.min.js'))
	
@app.route("/play/<name>")
def play(name):
	name=os.path.join('sounds', name)
	#print name
	if not pygame.mixer.get_int():
		pygame.mixer.init();
	fxchannel.play(Sound(name))
	#pygame.mixer.music.load(name)
	#pygame.mixer.music.play()
	##sounds[name].play()
	return "ok"

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname= User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_wrapper(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

def login_wrapper(user,remember_me):
	if pygame.mixer.music.get_busy():
		pygame.mixer.music.queue(user.themesong.filename)
	else:
		pygame.mixer.music.load(user.themesong.filename)
		pygame.mixer.music.play()
	
	login_user(user,remember=remember_me)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    posts = [
        { 'author': user, 'body': 'Test post #1' },
        { 'author': user, 'body': 'Test post #2' }
    ]
    return render_template('user.html',
        user = user,
        posts = posts)

class SoundModelView(ModelView):
	column_display_all_relations=True
	column_list = ('name', 'tags')
	form_excluded_columns = ('name')
	"""
	def is_accessible(self):
		if g.user is not None and g.user.is_admin():
			return True
		else:
			return False"""
	def on_model_change(self, form, model, is_created):
		

		if is_created==True:
			model.name=stripfilename(model.filename)
		self.session.add(model)



class SoundFileAdmin(FileAdmin):
	allowed_extensions=('wav', 'mp3', 'ogg')
	def is_accessible(self):
		if g.user is not None and g.user.is_admin():
			return True
		else:
			return False
	def on_file_upload(self, directory, path, filename):
		db.session.add(Sound(filename=filename))
		db.session.commit()

class ThemeSongFileAdmin(FileAdmin):
	allowed_extensions=('wav', 'mp3', 'ogg')
	def is_accessible(self):
		if g.user is not None and g.user.is_admin():
			return True
		else:
			return False
	def on_file_upload(self, directory, path, filename):
		db.session.add(ThemeSong(filename=filename))
		db.session.commit()

admin.add_view(SoundModelView(Sound, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(SoundFileAdmin(os.path.join(basedir, 'sounds'), '/sounds/', name = 'Sound Files'))
admin.add_view(ThemeSongFileAdmin(os.path.join(basedir, 'themes'), '/themes/', name = 'Theme Songs'))
