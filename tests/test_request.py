"""
Test placing a jumpseat request as a guest.
"""
import uuid
import re

from datetime import date
from datetime import timedelta

import pytest

import sqlalchemy as sa

from flask import session as flask_session
from flask import url_for
from flask_login import current_user

from jumpseat_request.extension import timezone
from jumpseat_request.model import Airline
from jumpseat_request.model import EmailJob
from jumpseat_request.model import EmailJobRecipient
from jumpseat_request.model import JumpseatRequest
from jumpseat_request.model import NotificationRule
from jumpseat_request.model import User
from jumpseat_request.signal import jumpseat_request_created
from jumpseat_request.signal import jumpseat_request_escalate

from tests.test_app import app
from tests.test_app import db
from tests.test_app import users

def get_airlines(db):
    query = sa.select(Airline)
    objects = db.session.scalars(query)
    airlines = {
        airline.icao_code: airline for airline in objects
    }
    return airlines

def update_application_settings(client):
    """
    Post form data to update required application settings.
    """
    response = client.post(
        url_for('app_settings.edit_required_settings'),
        data = {
            'from_address': 'from-address@company.com',
        },
        follow_redirects = True,
    )

def test_escalation_query(app, db):
    """
    Test that needs_escalation returns a proposal that exceeds the
    NotificationRule age condition.
    """
    # craft a proposal that matches escalation conditions
    notification_rule = NotificationRule(
        name = jumpseat_request_escalate.name,
        signal_name = jumpseat_request_escalate.name,
        created_at_age_seconds = 60 * 30,
    )
    db.session.add(notification_rule)

    airlines = get_airlines(db)
    jumpseat_request = JumpseatRequest(
        created_at = timezone.now() - timedelta(minutes=30),
        flight_number = 'AA1111',
        flight_date = timezone.now().date().isoformat(),
        employee_airline = airlines['ABX'],
        employee_number = 'EE1111',
        employee_email = 'first.last@company.com',
        request_by = User(
            email_address = 'first.last@company.com',
        ),
    )
    db.session.add(jumpseat_request)
    db.session.commit()

    escalates = JumpseatRequest.needs_escalation(timezone.now())
    assert len(escalates) == 1

    assert escalates == [(jumpseat_request, notification_rule)]

def test_reset_password(app, db, users):
    """
    Check that a user with the reset_password flag set is redirected to change
    their password.
    """
    with app.test_client() as client:
        # Ensure application settings are set.
        update_application_settings(client)

        user_need_password = users['reset_password_user']
        # Login as user needs password change.
        response = client.post(
            url_for('auth.login'),
            data = {
                'email_address': user_need_password.email_address,
                'password': 'password',
            },
            follow_redirects = True,
        )
        assert response.status_code == 200

        # Check redirect to change password
        response = client.get(
            # hit an endpoint that checks for reset password
            url_for('jumpseat_request.landing_page', user_id=users['admin'].id),
            follow_redirects = True,
        )
        assert response.status_code == 200
        assert '<input id="password"' in response.text

def test_require_admin(app, db, users):
    """
    Check admin pages redirect to login for insufficient privilege.
    """
    with app.test_client() as client:
        # Login as non-admin user
        user = users['user']
        response = client.post(
            url_for('auth.login'),
            data = {
                'email_address': user.email_address,
                'password': 'password',
            },
            follow_redirects = True,
        )
        assert response.status_code == 200
        assert 'Logged in' in response.text

        response = client.get(
            url_for('admin.user_list'),
            follow_redirects = True,
        )
        assert response.status_code == 200

        assert 'Admin login required' in response.text

def test_get_admin_pages(app, db, users):
    """
    Check for 200 response from all admin pages.
    """
    with app.test_client() as client:
        # Login as an admin
        response = client.post(
            url_for('auth.login'),
            data = {
                'email_address': users['admin'].email_address,
                'password': 'password',
            },
            follow_redirects = True,
        )
        assert response.status_code == 200

        # Should flash confirmation
        assert 'Logged in' in response.text

        # Check good response and expected text.
        # table name endpoints under admin with model names in the html
        names = [
            ('employee', 'Employee'),
            ('jumpseat_request', 'JumpseatRequest',),
            ('user', 'User'),
        ]
        for name, expected_text in names:
            endpoint = f'admin.{name}_list'
            response = client.get(url_for(endpoint), follow_redirects=True)
            assert response.status_code == 200

def test_create_jumpseat_request(app, db, users):
    """
    Check posting a jump seat request to the landing_page and that we generate emails.
    """
    airlines = get_airlines(db)
    with app.test_client() as client:
        # POST to login
        response = client.post(
            url_for('auth.login'),
            data = {
                'email_address': 'admin@company.com',
                'password': 'password',
            },
            follow_redirects = True,
        )
        assert response.status_code == 200
        assert 'Logged in' in response.text

        landing_url = url_for('jumpseat_request.landing_page')
        # POST a jumpseat request as a guest to the landing page without logging in.
        response = client.post(
            landing_url,
            data = {
                # JumpseatRequestSubform fields (via FormField named 'request')
                'flight_number': 'FLIGHT1',
                'flight_date': '2026-01-01',
                # EmployeeSubForm fields (via FormField named 'employee')
                'employee-airline': str(airlines['ABX'].id),
                'employee-name': 'First Last',
                'employee-employee_number': 'EE1111',
                'employee-email_address': 'user1111@company.com',
                'employee-phone': '111 111 1111',
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        # Check database for our data.
        query = (
            db.select(JumpseatRequest)
            .where(
                JumpseatRequest.flight_number == 'FLIGHT1',
                JumpseatRequest.flight_date == date(2026,1,1),
            )
        )
        exists = db.session.scalars(query).one_or_none()
        assert exists

        # Check email job objects created in database.
        query = (
            db.select(EmailJob)
            .join(EmailJobRecipient)
            .where(
                EmailJob.subject == 'Jump Seat Request',
                EmailJobRecipient.email_address == 'user1111@company.com',
            )
        )
        exists = db.session.scalars(query).one_or_none()
        assert exists

        # check our convenient link works
        # this would redirect us to login because we're guest, but shows the
        # rendered link in the email is good.
        pattern = r'<a href="(.*)">Click to approve or deny request</a>'
        match = re.search(pattern, exists.body_html)
        url = match.group(1)
        response = client.get(
            url,
            follow_redirects=True,
        )
        assert response.status_code == 200

        # Check our saved request autofills next load/get.
        response = client.get(landing_url)
