import frappe
from frappe import _
import json


@frappe.whitelist()
def get_app_config():
    """Get mobile app configuration"""
    config = {
        "app_name": "Bizaxl School Management",
        "app_version": "1.0.0",
        "api_version": "v1",
        "features": {
            "dashboard": True,
            "attendance": True,
            "fees": True,
            "exams": True,
            "timetable": True,
            "homework": True,
            "library": True,
            "hostel": True,
            "transport": True,
            "events": True,
            "certificates": True,
            "live_tracking": True,
            "notifications": True,
            "communication": True,
            "online_payment": True
        },
        "theme": {
            "primary_color": "#2c3e50",
            "secondary_color": "#3498db",
            "accent_color": "#e74c3c"
        },
        "pwa": {
            "enabled": True,
            "manifest_url": "/assets/school_management_software/manifest.json",
            "service_worker_url": "/assets/school_management_software/js/pwa.js"
        }
    }
    return config


@frappe.whitelist()
def get_notifications(user_id=None):
    """Get notifications for the current user"""
    if not user_id:
        user_id = frappe.session.user
    
    notifications = []
    
    # Get recent ToDos assigned to this user
    user_employee = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
    if user_employee:
        todos = frappe.get_all("ToDo",
            filters={
                "allocated_to": user_id,
                "status": "Open"
            },
            fields=["name", "description", "reference_type", "reference_name", "priority", "date"],
            order_by="date desc",
            limit=20
        )
        for todo in todos:
            notifications.append({
                "id": todo.name,
                "type": "task",
                "title": todo.description[:100] if todo.description else "Task",
                "reference_type": todo.reference_type,
                "reference_name": todo.reference_name,
                "priority": todo.priority,
                "date": str(todo.date or ""),
                "read": False
            })
    
    return notifications


@frappe.whitelist()
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    frappe.db.set_value("ToDo", notification_id, "status", "Closed")
    return {"success": True}


@frappe.whitelist()
def get_student_attendance_summary(student_id=None, month=None, year=None):
    """Get attendance summary for mobile display"""
    from frappe.utils import today, getdate, month_diff
    
    if not student_id:
        student_id = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    if not student_id:
        frappe.throw(_("Student not found"))
    
    import datetime
    now = datetime.datetime.now()
    if not month:
        month = now.month
    if not year:
        year = now.year
    
    month_start = "{0}-{1:02d}-01".format(year, month)
    if month == 12:
        month_end = "{0}-01-01".format(year + 1)
    else:
        month_end = "{0}-{1:02d}-01".format(year, month + 1)
    
    records = frappe.get_all("Student Attendance",
        filters={
            "student": student_id,
            "date": [">=", month_start],
            "date": ["<", month_end],
            "docstatus": 1
        },
        fields=["date", "status", "course"]
    )
    
    total = len(records)
    present = sum(1 for r in records if r.status == "Present")
    absent = sum(1 for r in records if r.status == "Absent")
    leave = total - present - absent
    
    return {
        "month": month,
        "year": year,
        "total_working_days": total,
        "present": present,
        "absent": absent,
        "leave": leave,
        "percentage": round((present / total * 100), 1) if total > 0 else 0,
        "records": records
    }


@frappe.whitelist()
def get_upcoming_events(limit=10):
    """Get upcoming school events"""
    events = frappe.get_all("School Event",
        filters={
            "date": [">=", frappe.utils.today()],
            "publish": 1
        },
        fields=["name", "title", "date", "time", "venue", "description", "event_type"],
        order_by="date asc",
        limit=limit
    )
    return events


@frappe.whitelist()
def get_live_bus_location(route_id=None):
    """Get live bus location for GPS tracking"""
    if not route_id:
        routes = frappe.get_all("Transport Route",
            fields=["name", "route_name", "vehicle"]
        )
        return {"routes": routes, "message": "Select a route to view live location"}
    
    route = frappe.get_doc("Transport Route", route_id)
    vehicle = route.vehicle
    
    # Get latest GPS tracking log for this vehicle
    latest_log = frappe.get_all("Vehicle GPS Tracking Log",
        filters={"vehicle": vehicle},
        fields=["latitude", "longitude", "timestamp", "speed", "status"],
        order_by="timestamp desc",
        limit=1
    )
    
    return {
        "route": route.route_name,
        "vehicle": vehicle,
        "current_location": latest_log[0] if latest_log else None,
        "stops": [
            {"name": s.stop_name, "order": s.stop_order, "time": str(s.estimated_time or "")}
            for s in route.stops
        ] if hasattr(route, 'stops') else []
    }


@frappe.whitelist()
def submit_leave_application(student_id, reason, from_date, to_date, leave_type="General"):
    """Submit a leave application from mobile"""
    if not student_id:
        student_id = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    
    leave = frappe.get_doc({
        "doctype": "Hostel Leaves" if frappe.db.exists("DocType", "Hostel Leaves") else "Leave Application",
        "student": student_id,
        "reason": reason,
        "from_date": from_date,
        "to_date": to_date,
        "leave_type": leave_type,
        "status": "Open"
    })
    leave.insert(ignore_permissions=True)
    
    return {"success": True, "leave_id": leave.name}


@frappe.whitelist()
def get_student_certificates(student_id=None):
    """Get certificates for a student"""
    if not student_id:
        student_id = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    
    certificates = frappe.get_all("Student Certificate",
        filters={"student": student_id},
        fields=["name", "student_name", "template", "generated_on", "status", "certificate_pdf"],
        order_by="generated_on desc"
    )
    return certificates


@frappe.whitelist()
def get_online_payment_link(invoice_id):
    """Get online payment link for an invoice"""
    # Use ERPNext payment gateway or generate payment link
    payment_url = "{0}/pay?invoice={1}".format(
        frappe.utils.get_url(),
        invoice_id
    )
    return {
        "payment_url": payment_url,
        "invoice": invoice_id,
        "gateway": "Razorpay"  # Configure based on your payment gateway
    }
