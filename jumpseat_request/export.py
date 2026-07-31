"""
Exporting related functionality.
"""
import openpyxl

def create_excel(jumpseat_requests, title=None):
    """
    Return a new openpyxl Workbook object from a list of jumpseat requests.
    """

    wb = openpyxl.Workbook()

    ws = wb.active

    # Header
    ws.append([
        'NOTES',
        'FLT NO',
        'DEPT',
        'ARRV',
        'EMPNO',
        'Employee Name',
        'Rank',
        'Company',
        'Priority',
        'Phone',
    ])

    for request in jumpseat_requests:
        ws.append([
            request.reason,
            request.flight_number,
            None, # DEPT
            None, # ARRV
            request.employee_number,
            None, # RANK
            request.employee_airline.iata_code,
            None, # Priority
            request.employee_phone,
        ])
