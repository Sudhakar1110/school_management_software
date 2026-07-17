# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VisitorLog(Document):
    """Track visitor entry and exit at school premises"""
    
    def before_insert(self):
        """Auto-set entry time if not provided"""
        if not self.entry_time:
            self.entry_time = frappe.utils.now_time()
