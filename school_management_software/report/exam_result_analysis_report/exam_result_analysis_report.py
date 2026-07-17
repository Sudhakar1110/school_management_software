# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    """Exam Result Analysis: Pass %, Average Score by Student Group and Course"""
    columns = [
        {"label": "Student Group", "fieldname": "student_group", "fieldtype": "Data", "width": 150},
        {"label": "Course", "fieldname": "course", "fieldtype": "Data", "width": 150},
        {"label": "Total Students", "fieldname": "total", "fieldtype": "Int", "width": 100},
        {"label": "Passed", "fieldname": "passed", "fieldtype": "Int", "width": 80},
        {"label": "Failed", "fieldname": "failed", "fieldtype": "Int", "width": 80},
        {"label": "Pass %", "fieldname": "pass_pct", "fieldtype": "Percent", "width": 80},
        {"label": "Average Score", "fieldname": "avg_score", "fieldtype": "Float", "width": 100}
    ]
    data = frappe.db.sql("""
        SELECT ar.student_group, ar.course,
               COUNT(*) AS total,
               SUM(CASE WHEN ar.grade IN ('A', 'B', 'C', 'Pass') THEN 1 ELSE 0 END) AS passed,
               SUM(CASE WHEN ar.grade IN ('D', 'F', 'Fail') THEN 1 ELSE 0 END) AS failed,
               ROUND(AVG(ar.score) * 100, 1) AS avg_score
        FROM `tabAssessment Result` ar
        GROUP BY ar.student_group, ar.course
        ORDER BY ar.student_group, ar.course
    """, as_dict=True)
    for d in data:
        d["pass_pct"] = round((d["passed"] / d["total"]) * 100, 1) if d["total"] > 0 else 0
    return columns, data
