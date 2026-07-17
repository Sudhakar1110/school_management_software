# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        _("Student") + ":Link/Student:150",
        _("Student Name") + "::200",
        _("Hostel") + ":Link/Hostel:150",
        _("Room") + ":Link/Hostel Room:120",
        _("Attendance Date") + ":Date:120",
        _("Status") + "::100",
        _("In Time") + "::100",
        _("Out Time") + "::100",
        _("Remarks") + "::200"
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    query = """
        SELECT
            ha.student,
            ha.student_name,
            ha.hostel,
            ha.hostel_room,
            ha.date,
            ha.status,
            ha.in_time,
            ha.out_time,
            ha.remarks
        FROM
            `tabHostel Attendance` ha
        WHERE
            ha.docstatus < 2
            {conditions}
        ORDER BY
            ha.date DESC
    """.format(conditions=conditions)
    return frappe.db.sql(query, filters, as_dict=1)

def get_conditions(filters):
    conditions = []
    if filters:
        if filters.get("from_date"):
            conditions.append("AND ha.date >= %(from_date)s")
        if filters.get("to_date"):
            conditions.append("AND ha.date <= %(to_date)s")
        if filters.get("hostel"):
            conditions.append("AND ha.hostel = %(hostel)s")
        if filters.get("status"):
            conditions.append("AND ha.status = %(status)s")
    return " " . join(conditions)
