# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BiometricDevice(Document):
    """Manage biometric/RFID attendance devices"""
    
    def validate(self):
        """Validate device configuration"""
        if self.ip_address and not self.port:
            self.port = 4370  # Default ZKTeco port
        
        if self.is_active and not self.ip_address and not self.api_endpoint:
            frappe.msgprint(
                frappe._("Warning: Active device has no IP address or API endpoint configured."),
                alert=True
            )
