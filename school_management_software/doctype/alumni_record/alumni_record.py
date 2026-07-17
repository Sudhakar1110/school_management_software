# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AlumniRecord(Document):
    """Record of graduated students for alumni management"""
    
    def before_insert(self):
        """Set defaults before creation"""
        if not self.graduation_year and self.date_of_leaving:
            self.graduation_year = frappe.utils.getdate(self.date_of_leaving).year
