import csv
import re
import sys

import click

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import logout_user
from markupsafe import Markup

from jumpseat_request.extension import db
from jumpseat_request.model import Rank

from htmlkit.lists import definition_list

export_bp = Blueprint('export', __name__)

export_bp.cli.help = 'Export data from database.'

tables = db.metadata.tables.values()

def pairs_from_pattern(table_pattern):
    """
    (Mapper, Table) pairs matching a table regex pattern.
    """
    mappers = db.Model.registry.mappers
    for mapper in sorted(mappers, key=lambda m: m.class_.__tablename__):
        table = mapper.tables[0]
        class_ = mapper.class_
        if table_pattern and not re.match(table_pattern, table.name):
            continue
        yield (mapper, table)

def get_columns(mapper):
    columns = [c for c in mapper.columns if c not in mapper.primary_key]
    return columns

@export_bp.cli.command('list')
@click.option('--table', 'table_pattern')
def list_table(table_pattern):
    """
    List table names from mapped classes.
    """
    for mapper, table in pairs_from_pattern(table_pattern):
        click.echo(table.name)
        continue
        columns = get_columns(mapper)
        query = db.select(*columns)
        
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        rows = db.session.execute(query).mappings().all()

        writer.writerows(rows)

@export_bp.cli.command('dump')
@click.option('--table', 'table_pattern')
@click.option('--output', required=True, default='{table}.csv')
def dump(table_pattern, output):
    for mapper, table in pairs_from_pattern(table_pattern):
        click.echo(table.name)

        columns = get_columns(mapper)
        query = db.select(*columns)

        output_filename = output.format(table=table)
        with open(output_filename, 'w', newline='', encoding='utf8') as output_file:
            fieldnames = [c.name for c in columns]
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            rows = db.session.execute(query).mappings().all()

            writer.writerows(rows)

        click.echo(f'Wrote {output_filename}')
