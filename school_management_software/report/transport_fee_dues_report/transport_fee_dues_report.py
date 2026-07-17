# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    """Transport Fee Dues Report"""
    columns = [
        {"label": "Student", "fieldname": "student", "fieldtype": "Link", "options": "Custom Student", "width": 120},
        {"label": "Student Name", "fieldname": "student_name", "fieldtype": "Data", "width": 150},
        {"label": "Route", "fieldname": "transport_route", "fieldtype": "Link", "options": "Transport Route", "width": 120},
        {"label": "Monthly Fee", "fieldname": "monthly_fee", "fieldtype": "Currency", "width": 100},
        {"label": "Fee Status", "fieldname": "fee_status", "fieldtype": "Data", "width": 100},
        {"label": "Academic Year", "fieldname": "academic_year", "fieldtype": "Data", "width": 100}
    ]
    conditions = "sta.is_active = 1 AND sta.fee_status IN ('Pending', 'Overdue', 'Partial')"
    if filters and filters.get("fee_status"):
        conditions += " AND sta.fee_status = '{0}'".format(filters["fee_status"])
    data = frappe.db.sql("""
        SELECT sta.student, sta.student_name, sta.transport_route,
               sta.monthly_fee, sta.fee_status, sta.academic_year
        FROM `tabStudent Transport Assignment` sta
        WHERE {0}
        ORDER BY sta.fee_status, sta.student_name
    """.format(conditions), as_dict=True)
    return columns, data
