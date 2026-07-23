import inspect

from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.views import View

from jumpseat_request.extension import db
class SingleView(View):
    """
    View a single object in dedicated page.
    """

    def __init__(
        self,
        template,
        model_class,
    ):
        self.template = template
        self.model_class = model_class

    def dispatch_request(self, **ident):
        instance = db.session.get(self.model_class, ident)
        if instance is None:
            abort(404, description=f'Instance not found {ident}')

        context = {
            'model_class': self.model_class,
            'instance': instance,
        }
        return render_template(self.template, **context)

class ListView(View):
    """
    Paginated list of objects inside a table.
    """

    methods = ['GET', 'POST']

    def __init__(
        self,
        template,
        model_class,
        pagination_getter,
        table,
        new_endpoint=None,
        edit_endpoint=None,
        form_class = None,
        note = None,
    ):
        self.template = template
        self.model_class = model_class
        self.pagination_getter = pagination_getter
        self.table = table
        self.new_endpoint = new_endpoint
        if edit_endpoint and not callable(edit_endpoint):
            raise ValueError(f'edit_endpoint {edit_endpoint} must be callable.')
        self.edit_endpoint = edit_endpoint
        self.note = note

    def dispatch_request(self):
        context = {
            'pagination': self.pagination_getter(),
            'pagination_doc': self.pagination_getter.__doc__,
            'table': self.table,
            'model_class': self.model_class,
            'new_endpoint': self.new_endpoint,
            'edit_endpoint': self.edit_endpoint,
            'note': self.note,
        }
        return render_template(self.template, **context)


class NewObjectView(View):

    methods = ['GET', 'POST']

    def __init__(
        self,
        template,
        model_class,
        form_class,
        after_endpoint = None,
    ):
        self.template = template
        self.model_class = model_class
        self.form_class = form_class
        self.after_endpoint = after_endpoint

    def dispatch_request(self):
        form = self.form_class()

        if form.validate_on_submit():
            instance = self.model_class()
            db.session.add(instance)
            form.populate_obj(instance)
            db.session.commit()
            flash(f'New {self.model_class.__tablename__} created', 'success')
            if self.after_endpoint:
                next_url = url_for(self.after_endpoint)
                return redirect(next_url)

        context = {
            'model_class': self.model_class,
            'form': form,
        }
        return render_template(self.template, **context)


class EditObjectView(View):

    methods = ['GET', 'POST']

    def __init__(
        self,
        template,
        model_class,
        form_class,
        kwargs_for_form = None,
        after_endpoint = None,
    ):
        self.template = template
        self.model_class = model_class
        self.form_class = form_class
        self.kwargs_for_form = kwargs_for_form
        self.after_endpoint = after_endpoint

    def dispatch_request(self, **ident):
        instance = db.session.get(self.model_class, ident)

        if instance is None:
            abort(404, description=f'Instance not found {kwargs}')

        form_class = self.form_class
        if inspect.isclass(form_class):
            pass
        elif callable(form_class):
            # Not a class but is callable.
            form_class = form_class()

        if request.method == 'GET':
            if self.kwargs_for_form:
                kwargs = self.kwargs_for_form()
            else:
                kwargs = {'obj': instance}
            form = form_class(**kwargs)

        elif request.method == 'POST':
            form = form_class(formdata=request.form, obj=instance)

            if form.validate():
                form.populate_obj(instance)
                db.session.commit()
                flash(f'{self.model_class.__tablename__} updated', 'success')
                if self.after_endpoint:
                    next_url = url_for(self.after_endpoint)
                    return redirect(next_url)

        context = {
            'model_class': self.model_class,
            'form_class': form_class,
            'form': form,
        }
        return render_template(self.template, **context)
