from wtforms import Form, fields, validators


class UserForm(Form):
    full_name = fields.TextField('Full Name', [validators.Required()])
    email = fields.TextField('Email', [validators.Required(), validators.Email()])