from sqlalchemy import Date
from sqlalchemy import cast
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FunctionElement

class trunc_date(FunctionElement):
    """
    Postgresql and Oracle compatible date truncation function.
    """
    type = Date()
    inherit_cache = True

@compiles(trunc_date)
def _trunc_default(element, compiler, **kwargs):
    return f'DATE({compiler.process(element.clauses)})'

@compiles(trunc_date, 'oracle')
def _trunc_oracle(element, compiler, **kwargs):
    return "TRUNC(%s)" % compiler.process(element.clauses, **kwargs)

@compiles(trunc_date, 'postgresql')
def _trunc_pg(element, compiler, **kwargs):
    return "DATE_TRUNC('day', %s)" % compiler.process(element.clauses, **kwargs)
