# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VehicleGPSTrackingLog(Document):
    """Log real-time GPS data from school transport vehicles"""
    
    def before_insert(self):
        """Auto-set driver name and route from vehicle"""
        if self.vehicle:
            vehicle = frappe.get_doc("Transport Vehicle", self.vehicle)
            self.driver_name = vehicle.driver_name if hasattr(vehicle, 'driver_name') else ""