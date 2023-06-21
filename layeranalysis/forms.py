from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CollectionAddressForm(FlaskForm):
    address = StringField(label='Collection Address: ',
                          validators=[
                           DataRequired(message='Collection address is required'),
                           Length(min=42, max=42, message='Collections contract address must be %(min)d characters')
                          ])
    submit = SubmitField(label='Fetch Collection Tx')
    save = SubmitField(label='Save')
    load = SubmitField(label='Load')
