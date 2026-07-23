import click

from flask import Blueprint

from jumpseat_request.extension import db
from jumpseat_request.model import Airline
from jumpseat_request.signal import jumpseat_request_signals

airline_bp = Blueprint('airline', __name__)

airline_bp.cli.help = 'Administrate airline database objects.'

@airline_bp.cli.command('create')
@click.option('--iata-code', required=True, help='Notification rule name.')
@click.option('--icao-code', required=True, help='Notification comment.')
def create_airline(iata_code, icao_code):
    """
    Create airline object.
    """
    airline = Airline(
        iata_code = iata_code,
        icao_code = icao_code,
    )
    db.session.add(airline)
    db.session.commit()
