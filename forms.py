# actual forms for objects... required if using Flask admin.
# the Mongo DB still comes first!
# any new forms must graft onto forms of boilerplate, watch namespace conflicts, etc.

from flask import g
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                     BooleanField, TextAreaField, HiddenField, SelectField)
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from werkzeug.security import generate_password_hash
#from utils import slugify
import os

