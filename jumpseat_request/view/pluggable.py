from flask import render_template
from flask import request
from flask.views import View

from jumpseat_request.extension import db

class TableEditor(View):

    methods = ['GET', 'POST']

    def __init__(self, template, model_class, pagination_getter, table):
        self.template = template
        self.model_class = model_class
        self.pagination_getter = pagination_getter
        self.table = table

    @classmethod
    def from_model(cls, model):
        pagination_getter = lambda: db.paginate(db.select(model))
        return 

    def dispatch_request(self):
        context = {
            'objects': self.pagination_getter(self.model_class),
            'table': self.table,
            'model_class': self.model_class,
        }
        return render_template(self.template, **context)
