from .airline import EditAirlineForm
from .airline import NewAirlineForm
from .announcement import EditAnnouncementForm
from .announcement import NewAnnouncementForm
from .application_setting import EditApplicationSettingForm
from .employee import EditEmployeeForm
from .employee import EmployeeSubForm
from .employee import NewEmployeeForm
from .jumpseat_request import EditJumpseatRequestAdminForm
from .jumpseat_request import EditJumpseatRequestForm
from .jumpseat_request import JumpseatRequestActionForm
from .jumpseat_request import NewJumpseatRequestForm
from .login import LoginForm
from .notification import EditNotificationRuleForm
from .notification import NotificationRecipientSubform
from .user import ChangePassword
from .user import EditAccountForm
from .user import EditUserForm
from .user import NewUserForm
from .user import RegisterUserForm
from .verify_email import VerifyEmailForm

def form_obj_diff(form, obj):
    changes = {}

    # different values for field name
    for field in form:
        if hasattr(obj, field.name):
            value = getattr(obj, field.name)
            if value != field.data:
                changes[field.name] = (value, field.data)

    return changes

model_class_forms = {
    'Airline': {
        'new': NewAirlineForm,
        'edit': EditAirlineForm,
    },
    'Announcement': {
        'new': NewAnnouncementForm,
        'edit': EditAnnouncementForm,
    },
    'Employee': {
        'new': NewEmployeeForm,
        'edit': EditEmployeeForm,
    },
    'JumpseatRequest': {
        'new': NewJumpseatRequestForm,
        'edit': EditJumpseatRequestForm,
    },
    'NotificationRule': {
        'edit': EditNotificationRuleForm,
    },
    'User': {
        'new': NewUserForm,
        'edit': EditUserForm,
    },
}
