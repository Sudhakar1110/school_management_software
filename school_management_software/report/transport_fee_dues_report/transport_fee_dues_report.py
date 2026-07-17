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
        _("Transport Fee ID") + ":Link/Transport Fee:180",
        _("Student") + ":Link/Student:150",
        _("Student Name") + "::200",
        _("Route") + ":Link/Transport Route:180",
        _("Vehicle") + ":Link/Transport Vehicle:150",
        _("Fee Amount") + ":Currency:120",
        _("Paid Amount") + ":Currency:120",
        _("Outstanding") + ":Currency:120",
        _("Due Date") + ":Date:100",
        _("Status") + "::120"
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    query = """
        SELECT
            tf.name,
            tf.student,
            tf.student_name,
            tf.transport_route,
            tf.transport_vehicle,
            tf.amount,
            tf.paid_amount,
            (tf.amount - IFNULL(tf.paid_amount, 0)) as outstanding,
            tf.due_date,
            tf.status
        FROM
            `tabTransport Fee` tf
        WHERE
            tf.docstatus < 2
            {conditions}
        ORDER BY
            tf.due_date ASC
    """.format(conditions=conditions)
    return frappe.db.sql(query, filters, as_dict=1)

def get_conditions(filters):
    conditions = []
    if filters:
        if filters.get("from_date"):
            conditions.append("AND tf.due_date >= %(from_date)s")
        if filters.get("to_date"):
            conditions.append("AND tf.due_date <= %(to_date)s")
        if filters.get("status"):
            conditions.append("AND tf.status = %(status)s")
        if filters.get("transport_route"):
            conditions.append("AND tf.transport_route = %(transport_route)s")
    return " " . join(conditions)
