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
        _("Issue ID") + ":Link/Book Issue:180",
        _("Library Member") + ":Link/Library Member:150",
        _("Book") + ":Link/Library Book:200",
        _("Book Copy") + ":Link/Book Copy:120",
        _("Issue Date") + ":Date:100",
        _("Due Date") + ":Date:100",
        _("Return Date") + ":Date:100",
        _("Issue Status") + "::120",
        _("Fine Amount") + ":Currency:100"
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    query = """
        SELECT
            bi.name,
            bi.library_member,
            bi.library_book,
            bi.book_copy,
            bi.issue_date,
            bi.due_date,
            bi.return_date,
            bi.issue_status,
            COALESCE((
                SELECT SUM(lf.amount)
                FROM `tabLibrary Fine` lf
                WHERE lf.book_return = (
                    SELECT br.name FROM `tabBook Return` br
                    WHERE br.book_issue = bi.name LIMIT 1
                )
            ), 0) as fine_amount
        FROM
            `tabBook Issue` bi
        WHERE
            bi.docstatus < 2
            {conditions}
        ORDER BY
            bi.issue_date DESC
    """.format(conditions=conditions)
    return frappe.db.sql(query, filters, as_dict=1)

def get_conditions(filters):
    conditions = []
    if filters:
        if filters.get("from_date"):
            conditions.append("AND bi.issue_date >= %(from_date)s")
        if filters.get("to_date"):
            conditions.append("AND bi.issue_date <= %(to_date)s")
        if filters.get("issue_status"):
            conditions.append("AND bi.issue_status = %(issue_status)s")
    return " " . join(conditions)
