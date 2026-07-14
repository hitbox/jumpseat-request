from flask import current_app


class AirlineLabelGetter:

    def __init__(self, config_key='JUMPSEAT_REQUEST_SHOW_AIRLINE_CODE', default='icao_code'):
        self.config_key = config_key
        self.default = default

    def __call__(self, airline):
        attr = current_app.config.get(self.config_key, self.default)
        return getattr(airline, attr)


class ConfigSetting:

    def __init__(self, config_key):
        self.config_key = config_key
        self.config_value = None

    def __call__(self, *args, **kwargs):
        if self.config_value is None:
            if self.config_key not in current_app.config:
                raise KeyError(f'{self.config_key!r} must be in config')
            self.config_value = current_app.config[self.config_key]
        return self.config_value


def airline_label_attribute():
    key = 'JUMPSEAT_REQUEST_SHOW_AIRLINE_CODE'
    if key not in current_app.config:
        raise KeyError(f'{key} must be in config')
    return current_app.config.get(key, 'icao_code')

def from_address():
    """
    From-address email address as configured.
    """
    from .model import ApplicationSetting
    from .model.application_setting import ApplicationSettingEnum
    return ApplicationSetting.by_name(ApplicationSettingEnum.FROM_ADDRESS.name)

def datetime_format():
    """
    Return the configured datetime format.
    """
    key = 'JUMPSEAT_REQUEST_DATETIME_FORMAT'
    from_address = current_app.config[key]
    return from_address

def date_format():
    """
    Return the configured datetime format.
    """
    key = 'JUMPSEAT_REQUEST_DATE_FORMAT'
    from_address = current_app.config[key]
    return from_address

def default_endpoint():
    key = 'JUMPSEAT_REQUEST_DEFAULT_ENDPOINT'
    from_address = current_app.config.get(key, 'jumpseat_request.landing_page')
    return from_address

def context():
    return {
        'airline_label_attribute': airline_label_attribute(),
        'from_address': from_address(),
        'datetime_format': datetime_format(),
        'date_format': date_format(),
        'from_address': from_address(),
    }
