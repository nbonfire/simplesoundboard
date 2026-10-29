from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import User


class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])
    themesong = TextAreaField('themesong', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname=None, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate_nickname(self, field):
        if field.data == self.original_nickname:
            return
        if User.query.filter_by(nickname=field.data).first() is not None:
            raise ValidationError('This nickname is already in use. Please choose another one.')
