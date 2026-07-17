# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

from frappe.model.document import Document

class BoardMeeting(Document):
    """Manage board meetings, agendas, minutes and resolutions"""
    
    def on_submit(self):
        """When meeting is completed, mark as completed"""
        if self.meeting_status == "Scheduled" or self.meeting_status == "In Progress":
            self.meeting_status = "Completed"
