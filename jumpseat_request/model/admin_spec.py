from dataclasses import dataclass
from dataclasses import field

from jumpseat_request.view.pluggable import EditObjectView
from jumpseat_request.view.pluggable import ListView
from jumpseat_request.view.pluggable import NewObjectView

@dataclass
class AdminSpec:
    """
    Configuration for an admin pluggable view.
    """

    view_class: View = field(
        metadata = {
            'description':
                'Pluggable flask view for listing model_class instances.',
        },
    )

    html_table: Table = field(
        metadata = {
            'description':
                'htmlkit.Table class to render an html table'
                ' for listing instances.',
        },
    )

    pagination_getter: type = field(
        metadata = {
            'description':
                'Callable to return a flask_sqlalchemy.SQLAlchemy'
                ' Pagination object for list view.'
        }
    )

    list_rule: Optional[str] = field(
        default = None,
        metadata = {
            'description':
                'Flask url rule string for the list view.',
        }
    )

    list_endpoint: Optional[str] = field(
        default = None,
        metadata = {
            'description':
                'url rule for view_class',
        }
    )

    model_class: type = field(
        default = None,
        metadata = {
            'description': 'SQLAlchemy model class',
        },
    )

    name: Optional[str] = field(
        default = None,
        metadata = {
            'description': 'Name to use to build endpoint names.',
        }
    )

    template: Optional[str] = field(
        default = 'admin/table.html',
        metadata = {
            'description':
                'Jinja template name for rendering list of objects'
                ' from the model_clas.',
        }
    )

    edit_view_class: Optional[View] = field(
        default = None,
        metadata = {
            'description':
                'View class to edit instances of model_class.'
        }
    )

    edit_template: Optional[str] = field(
        default = 'admin/edit_form.html',
        metadata = {
            'description':
                'Jinja template name for rendering and edit form for instances'
                ' of model_class.'
        }
    )

    edit_form: Optional[FlaskForm] = field(
        default = None,
        metadata = {
            'description':
                'FlaskForm class to edit instances of model_class.'
        }
    )

    edit_endpoint: Optional[str] = field(
        default = None,
        metadata = {
            'description':
                'Endpoint to edit instances of model_class.'
        }
    )

    edit_rule: Optional[str] = field(
        default = None,
        metadata = {
            'description':
                'Flask URL rule for editing an instance of model_class.'
        }
    )

    edit_kwargs_for_form: Optional[dict] = field(
        default = None,
        metadata = {
            'description':
                'Flask URL rule for editing an instance of model_class.'
        }
    )

    after_endpoint: Optional[str] = field(
        default = None,
        metadata = {
            'description':
                'Endpoint to redirect after editing.'
        }
    )

    new_form: Optional[FlaskForm] = field(
        default = None,
        metadata = {
            'description':
                'FlaskForm class to create an new instance of model_class.'
        }
    )

    def __post_init__(self):
        if self.model_class and self.name is None:
            # table name is default name if not given
            self.name = self.model_class.__tablename__

        if self.name and self.list_endpoint is None:
            self.list_endpoint = f'{self.name}_list'
            if self.after_endpoint is None:
                self.after_endpoint = self.list_endpoint

        if self.list_rule is None:
            self.list_rule = f'/{self.name}'

        if self.name and self.edit_rule is None:
            self.edit_rule = f'/{self.name}/<id>'
