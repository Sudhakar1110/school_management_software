# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    """Hostel Attendance Summary"""
    columns = [
        {"label": "Hostel", "fieldname": "hostel", "fieldtype": "Data", "width": 120},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "Total Students", "fieldname": "total", "fieldtype": "Int", "width": 100},
        {"label": "Present", "fieldname": "present", "fieldtype": "Int", "width": 80},
        {"label": "Absent", "fieldname": "absent", "fieldtype": "Int", "width": 80},
        {"label": "Attendance %", "fieldname": "attendance_pct", "fieldtype": "Percent", "width": 100}
    ]
    data = frappe.db.sql("""
        SELECT ha.hostel, ha.date,
               COUNT(*) AS total,
               SUM(CASE WHEN ha.status = 'Present' THEN 1 ELSE 0 END) AS present,
               SUM(CASE WHEN ha.status = 'Absent' THEN 1 ELSE 0 END) AS absent
        FROM `tabHostel Attendance` ha
        GROUP BY ha.hostel, ha.date
        ORDER BY ha.date DESC, ha.hostel
    """, as_dict=True)
    for d in data:
        d["attendance_pct"] = round((d["present"] / d["total"]) * 100, 1) if d["total"] > 0 else 0
    return columns, data
