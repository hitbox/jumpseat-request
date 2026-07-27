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


@compiles(trunc_date, 'oracle')
def _trunc_oracle(element, compiler, **kw):
    return "TRUNC(%s)" % compiler.process(element.clauses, **kw)

@compiles(trunc_date, 'postgresql')
def _trunc_pg(element, compiler, **kw):
    return "DATE_TRUNC('day', %s)" % compiler.process(element.clauses, **kw)
