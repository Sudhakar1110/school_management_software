# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    """Mess Attendance & Meal Count Report"""
    columns = [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "Meal Type", "fieldname": "meal_type", "fieldtype": "Data", "width": 100},
        {"label": "Total Students", "fieldname": "total", "fieldtype": "Int", "width": 100},
        {"label": "Present", "fieldname": "present", "fieldtype": "Int", "width": 80},
        {"label": "Absent", "fieldname": "absent", "fieldtype": "Int", "width": 80}
    ]
    data = frappe.db.sql("""
        SELECT ma.date, ma.meal_type,
               COUNT(*) AS total,
               SUM(CASE WHEN ma.status = 'Present' THEN 1 ELSE 0 END) AS present,
               SUM(CASE WHEN ma.status = 'Absent' THEN 1 ELSE 0 END) AS absent
        FROM `tabMess Attendance` ma
        GROUP BY ma.date, ma.meal_type
        ORDER BY ma.date DESC, ma.meal_type
    """, as_dict=True)
    return columns, data
