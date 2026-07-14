import uuid

from flask import render_template
from flask import request
from flask import url_for
from flask_wtf import FlaskForm
from markupsafe import Markup
from sqlalchemy.ext.hybrid import hybrid_property
from wtforms import SubmitField

from jumpseat_request import settings
from jumpseat_request.extension import db
from jumpseat_request.extension import timezone

from .application_setting_enum import ApplicationSettingEnum
from .mixin import ModelMixin
from .user import User

class ApplicationSetting(db.Model, ModelMixin):
    """
    Key-value record for an application setting.
    """

    name = db.Column(
        db.String,
        primary_key = True,
    )

    value = db.Column(db.String)

    @classmethod
    def by_name(cls, name):
        """
        Return the value of setting by it's name from the database.
        """
        stmt = db.select(cls).where(cls.name == name)
        setting = db.session.scalars(stmt).one_or_none()
        if setting:
            return setting.value

    @classmethod
    def missing_settings(cls):
        missing = []
        for member in ApplicationSettingEnum:
            value = cls.by_name(member.name)
            if value is None:
                missing.append((member.name, member.form_field))
        return missing

    @classmethod
    def missing_settings_form(cls):
        missing = cls.missing_settings()
        if missing:
            class SettingsForm(FlaskForm):
                """
                Application settings initialization form
                """
                update = SubmitField()

                def save(self):
                    for member in ApplicationSettingEnum:
                        field = getattr(self, member.name.lower(), None)
                        if field:
                            setting = cls(name=member.name, value=field.data)
                            db.session.add(setting)

            for name, field in missing:
                setattr(SettingsForm, name.lower(), field)

            return SettingsForm
