# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today

class ComplianceCertification(Document):
    """Manage compliance certifications and track renewal schedules"""
    
    def before_save(self):
        """Auto-calculate status and send alerts if expiring soon"""
        if self.expiry_date:
            from frappe.utils import date_diff
            days_to_expiry = date_diff(self.expiry_date, today())
            
            if days_to_expiry < 0:
                self.status = "Expired"
                self.is_compliant = 0
            elif days_to_expiry < 90:
                self.status = "Pending Renewal"
                if not self.renewal_date:
                    self.renewal_date = self.expiry_date
                frappe.msgprint(
                    f"Alert: {self.certification_name} expires in {days_to_expiry} days. "
                    f"Please initiate renewal process."
                )
