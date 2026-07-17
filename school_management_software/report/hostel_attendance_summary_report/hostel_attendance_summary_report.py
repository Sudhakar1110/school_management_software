# Copyright (c) 2025, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        _("ID") + ":Link/Hostel Attendance:200",
        _("Status") + "::150",
        _("Date") + ":Date:120",
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    query = """
        SELECT
            name,
            status,
            modified
        FROM
            `tabHostel Attendance`
        WHERE
            docstatus < 2
            {conditions}
        ORDER BY
            modified DESC
    """.format(conditions=conditions or "")
    return frappe.db.sql(query, filters)


def get_conditions(filters):
    conditions = []
    if filters and filters.get("from_date"):
        conditions.append("AND modified >= %(from_date)s")
    if filters and filters.get("to_date"):
        conditions.append("AND modified <= %(to_date)s")
    return " ".join(conditions)
