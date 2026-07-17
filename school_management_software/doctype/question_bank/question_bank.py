# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class QuestionBank(Document):
    """Question bank for creating quizzes, worksheets, and assessments"""
    
    def validate(self):
        """Validate question bank entry"""
        if self.question_type in ("Multiple Choice", "True/False") and not self.options:
            frappe.msgprint(
                frappe._("Please provide options for {0} question.").format(self.question_type),
                alert=True
            )
