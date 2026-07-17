# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    """Library Circulation Report - Track issued books and overdue items"""
    columns = [
        {"label": "Book", "fieldname": "book", "fieldtype": "Link", "options": "Library Book", "width": 150},
        {"label": "Copy", "fieldname": "book_copy", "fieldtype": "Data", "width": 80},
        {"label": "Member", "fieldname": "library_member", "fieldtype": "Link", "options": "Library Member", "width": 120},
        {"label": "Issue Date", "fieldname": "issue_date", "fieldtype": "Date", "width": 100},
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": "Overdue Days", "fieldname": "overdue_days", "fieldtype": "Int", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100}
    ]
    data = frappe.db.sql("""
        SELECT bi.book, bi.book_copy, bi.library_member,
               bi.issue_date, bi.due_date,
               CASE WHEN bi.due_date < CURDATE() THEN DATEDIFF(CURDATE(), bi.due_date) ELSE 0 END AS overdue_days,
               bi.status
        FROM `tabBook Issue` bi
        WHERE bi.status = 'Issued'
        ORDER BY bi.due_date ASC
    """, as_dict=True)
    return columns, data
