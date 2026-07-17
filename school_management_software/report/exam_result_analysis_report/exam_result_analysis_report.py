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
        _("Student Name") + "::200",
        _("Student Group") + ":Link/Student Group:180",
        _("Exam Term") + ":Link/Exam Term:150",
        _("Academic Year") + ":Link/Academic Year:120",
        _("Assessment Group") + ":Link/Assessment Group:180",
        _("Total Marks") + ":Float:100",
        _("Percentage") + "::100",
        _("Class Rank") + "::100",
        _("School Rank") + "::100",
        _("Status") + "::100"
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    query = """
        SELECT
            sr.student_name,
            sr.student_group,
            sr.exam_term,
            sr.academic_year,
            sr.assessment_group,
            sr.total_marks,
            sr.percentage,
            sr.class_rank,
            sr.school_rank,
            sr.status
        FROM
            `tabStudent Rank` sr
        WHERE
            sr.docstatus < 2
            {conditions}
        ORDER BY
            sr.percentage DESC
    """.format(conditions=conditions)
    return frappe.db.sql(query, filters, as_dict=1)

def get_conditions(filters):
    conditions = []
    if filters:
        if filters.get("exam_term"):
            conditions.append("AND sr.exam_term = %(exam_term)s")
        if filters.get("student_group"):
            conditions.append("AND sr.student_group = %(student_group)s")
        if filters.get("academic_year"):
            conditions.append("AND sr.academic_year = %(academic_year)s")
        if filters.get("status"):
            conditions.append("AND sr.status = %(status)s")
    return " " . join(conditions)
