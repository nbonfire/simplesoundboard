from app import db
from hashlib import md5

ROLE_USER = 0
ROLE_ADMIN = 1

sound_tags_table = db.Table('sound_tags', db.Model.metadata,
						db.Column('sound_id', db.Integer, db.ForeignKey('sound.id')),
						db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
						)

class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.Unicode(64))

	def __str__(self):
		return self.name

class Sound(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	filename=db.Column(db.String(120))
	name=db.Column(db.String(120))
	tags = db.relationship('Tag', secondary=sound_tags_table, backref=db.backref('sounds', lazy='dynamic'))
	def __init__(self, filename=None, name=None):
		if filename==None:
			print "filename is none for some reason. %s" % self
		else:
			self.filename = filename
			if name == None:

				self.name = stripfilename(filename)
			else:
				self.name = name
	def __str__(self):
		return self.name

class ThemeSong(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	filename=db.Column(db.String(120))
	name=db.Column(db.String(120))
	users=relationship("User", backref='themesong')
	def __init__(self, filename=None, name=None):
		if filename==None:
			print "filename is none for some reason. %s" % self
		else:
			self.filename = filename
			if name == None:

				self.name = stripfilename(filename)
			else:
				self.name = name
	def __str__(self):
		return self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    #posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    themesong_id=db.ForeignKey('themesong.id')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User', 
        secondary = followers, 
        primaryjoin = (followers.c.follower_id == id), 
        secondaryjoin = (followers.c.followed_id == id), 
        backref = db.backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=identicon&r=x&s=' + str(size)

    def is_authenticated(self):
        return True

    def is_admin(self):
    	return bool(self.role == "ADMIN")

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname

    def __repr__(self):
        return '<User %r>' % (self.nickname)

def stripfilename(filename):
	basename=os.path.basename(filename)
	noextension=os.path.splitext(basename)[0] 
	separateCamelCase = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', noextension)
	return separateCamelCase.replace("_"," ")