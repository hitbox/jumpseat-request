from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField

class EditApplicationSettingForm(FlaskForm):
    """
    Application settings initialization form
    """

    name = StringField(
        render_kw = {
            'read-only': True,
        },
    )

    value = StringField()

    update = SubmitField()

    def populate_obj(self, obj):
        from jumpseat_request.extension import db
        from jumpseat_request.model import ApplicationSetting
        from jumpseat_request.model import ApplicationSettingEnum

        instance = db.session.get(ApplicationSetting, {'name': self.name.data})
        instance.value = self.value.data
