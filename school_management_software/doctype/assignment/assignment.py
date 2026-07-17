# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Assignment(Document):
    """Track assignments and submissions for students"""
    
    def validate(self):
        """Validate assignment fields"""
        if self.due_date and self.due_date <= frappe.utils.now_datetime():
            frappe.msgprint(
                frappe._("Warning: Due date is in the past."),
                alert=True
            )
        
        # Validate max_score
        if self.max_score and self.max_score <= 0:
            frappe.throw(frappe._("Maximum score must be greater than zero."))
