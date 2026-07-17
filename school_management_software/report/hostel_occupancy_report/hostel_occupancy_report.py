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
        _("Hostel") + ":Link/Hostel:150",
        _("Block") + ":Link/Hostel Block:120",
        _("Room") + ":Link/Hostel Room:150",
        _("Room Number") + "::120",
        _("Room Type") + ":Link/Hostel Room Types:120",
        _("Total Beds") + ":Int:100",
        _("Occupied Beds") + ":Int:100",
        _("Available Beds") + ":Int:100",
        _("Room Status") + "::120"
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    query = """
        SELECT
            hr.hostel,
            hr.hostel_block,
            hr.name,
            hr.room_number,
            hr.room_type,
            hr.total_beds,
            hr.occupied_beds,
            hr.available_beds,
            hr.room_status
        FROM
            `tabHostel Room` hr
        WHERE
            hr.docstatus < 2
            {conditions}
        ORDER BY
            hr.hostel, hr.hostel_block, hr.room_number
    """.format(conditions=conditions)
    return frappe.db.sql(query, filters, as_dict=1)

def get_conditions(filters):
    conditions = []
    if filters:
        if filters.get("hostel"):
            conditions.append("AND hr.hostel = %(hostel)s")
        if filters.get("room_status"):
            conditions.append("AND hr.room_status = %(room_status)s")
    return " " . join(conditions)
