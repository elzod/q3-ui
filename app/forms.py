from flask_wtf import Form
from wtforms import StringField, BooleanField, DateField
from wtforms.validators import DataRequired
import datetime

class ReservationForm(Form):
    server_name = StringField('server_name', validators=[DataRequired()])
    user_name = StringField('user_name', validators=[DataRequired()])
    start_date = StringField('start_date', validators=[DataRequired()])
    end_date = StringField('end_date', validators=[DataRequired()])		
