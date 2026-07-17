# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CourseModule(Document):
    """Course module for structured learning path (LMS)"""
    
    def validate(self):
        """Validate module ordering"""
        if not self.module_number:
            # Auto-assign next module number
            last_module = frappe.db.get_value(
                "Course Module",
                {"course": self.course},
                "max(module_number)"
            )
            self.module_number = (last_module or 0) + 1
