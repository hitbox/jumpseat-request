import uuid

from operator import attrgetter

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

def get_base_settings_form():
    class SettingsForm(FlaskForm):
        """
        Application settings initialization form
        """
        update = SubmitField()

        def populate_obj(self, application_setting):
            # ignore object and update database rows
            for member in ApplicationSettingEnum:
                field = getattr(self, member.name.lower(), None)
                if field:
                    instance = db.session.get(ApplicationSetting, {'name': member.name})
                    if instance:
                        # Update existing setting
                        instance.value = field.data
                    else:
                        # Add new setting
                        instance = ApplicationSetting(
                            name = member.name,
                            value = field.data,
                        )
                        db.session.add(instance)

    return SettingsForm


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
    def as_data(cls):
        return {obj.name.lower(): obj.value for obj in db.session.scalars(db.select(cls))}

    @classmethod
    def get_settings_form(cls):
        SettingsForm = get_base_settings_form()
        # Add fields
        members = sorted(ApplicationSettingEnum, key=attrgetter('name'))
        for member in members:
            field = member.form_field
            attr = member.name.lower()
            setattr(SettingsForm, attr, field)

            # Update values
            ident = {'name': member.name}
            setting = db.session.get(cls, ident)
            field.data = setting.value

        return SettingsForm

    @classmethod
    def missing_settings_form(cls):
        missing = cls.missing_settings()
        if missing:
            SettingsForm = get_base_settings_form()

            for name, field in missing:
                setattr(SettingsForm, name.lower(), field)

            return SettingsForm

    @classmethod
    def name_for_template(cls):
        return 'Application Settings'
