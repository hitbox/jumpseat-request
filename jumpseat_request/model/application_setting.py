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

def make_settings_form():
    class SettingsForm(FlaskForm):
        """
        Application settings initialization form
        """
        update = SubmitField()

        def populate_obj(self, application_setting):
            # ignore object and update database rows
            for member in ApplicationSettingEnum:
                field = getattr(self, member.name, None)
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

        def update_from_data(self, data):
            """
            Update from the view where all settings are presented as one form.
            """
            breakpoint()
            db.session.execute(
                db.update(ApplicationSetting),
                [
                    {'name': name, 'value': value}
                    for name, value in data.items()
                ]
            )

    return SettingsForm

def make_full_settings_form():
    form_class = make_settings_form()

    for member in ApplicationSettingEnum:
        setattr(form_class, member.name.lower(), member.form_field)

    return form_class

def make_empty_settings_form():
    return make_settings_form()


class ApplicationSetting(db.Model, ModelMixin):
    """
    Application settings as key-value records.
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
        """
        Return application settings from enum that are missing from the database.
        """
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
        SettingsForm = make_empty_settings_form()
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
            SettingsForm = make_empty_settings_form()

            for name, field in missing:
                setattr(SettingsForm, name.lower(), field)

            return SettingsForm

    @classmethod
    def name_for_template(cls):
        return 'Application Settings'

    @classmethod
    def full_settings_form(cls):
        return make_full_settings_form()
