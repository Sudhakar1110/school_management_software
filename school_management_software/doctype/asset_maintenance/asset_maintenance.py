# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

from frappe.model.document import Document

class AssetMaintenance(Document):
    """Track maintenance history and schedule for school assets"""
    
    def on_submit(self):
        """Update asset condition when maintenance is completed"""
        if self.status == "Completed" and self.asset_code:
            from frappe.model.document import Document
            asset = frappe.get_doc("Asset Register", self.asset_code)
            asset.condition = "Good"
            asset.save(ignore_permissions=True)
