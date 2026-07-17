import frappe
from frappe import _

@frappe.whitelist()
def get_student_dashboard(student_id=None):
    """Get student dashboard data for mobile/portal"""
    if not student_id:
        student_id = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    
    if not student_id:
        frappe.throw(_("Student not found for current user"))
    
    student = frappe.get_doc("Student", student_id)
    
    # Recent attendance (last 30 days)
    attendance = frappe.get_all("Student Attendance", 
        filters={"student": student.name, "docstatus": 1}, 
        fields=["date", "status"], 
        order_by="date desc", 
        limit=30
    )
    
    present_days = sum(1 for a in attendance if a.status == "Present")
    total_days = len(attendance)
    attendance_pct = round((present_days / total_days) * 100, 1) if total_days > 0 else 0
    
    # Upcoming exams
    upcoming_exams = frappe.get_all("Exam Schedule", 
        filters={"exam_date": [">=", frappe.utils.today()]}, 
        fields=["subject", "exam_date", "from_time", "to_time", "exam_hall"], 
        order_by="exam_date asc", 
        limit=5
    )
    
    # Fee summary
    fee_summary = {
        "total_payable": getattr(student, 'total_fee_payable', 0),
        "total_paid": getattr(student, 'total_fee_paid', 0),
        "balance": getattr(student, 'fee_balance', 0)
    }
    
    return {
        "student_name": student.student_name,
        "class": student.class_name,
        "section": student.section_name,
        "roll_no": student.roll_no,
        "register_no": student.register_no,
        "email": student.student_email_id,
        "image": student.image,
        "attendance": {
            "present": present_days,
            "total": total_days,
            "percentage": attendance_pct
        },
        "upcoming_exams": upcoming_exams,
        "fee_summary": fee_summary
    }


@frappe.whitelist()
def get_parent_dashboard():
    """Get parent dashboard data - shows all linked students"""
    guardian = frappe.db.get_value("Guardian Profile", {"user": frappe.session.user}, "name")
    
    if not guardian:
        # Try ERPNext Guardian
        guardian = frappe.db.get_value("Guardian", {"user": frappe.session.user}, "name")
    
    if not guardian:
        frappe.throw(_("Guardian profile not found for current user"))
    
    guardian_doc = frappe.get_doc("Guardian" if not frappe.db.exists("Guardian Profile", guardian) else "Guardian Profile", guardian)
    
    # Get students linked to this guardian
    students = []
    student_records = guardian_doc.get("students") or []
    
    for s in student_records:
        student_id = s.student
        student = frappe.get_doc("Student", student_id)
        
        students.append({
            "name": student.student_name,
            "class": getattr(student, 'class_name', ''),
            "roll_no": getattr(student, 'roll_no', ''),
            "image": getattr(student, 'image', ''),
            "email": getattr(student, 'student_email_id', '')
        })
    
    return {
        "guardian_name": guardian_doc.get("guardian_name") or guardian_doc.get("name"),
        "students": students
    }


@frappe.whitelist()
def get_timetable(student_id=None):
    """Get student timetable"""
    if not student_id:
        student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    else:
        student = student_id
    
    if not student:
        frappe.throw(_("Student not found"))
    
    # Get student group for the student
    enrollment = frappe.db.get_value("Program Enrollment",
        {"student": student, "docstatus": 1}, "student_group")
    
    if not enrollment:
        return {"days": []}
    
    # Get course schedule
    schedule = frappe.get_all("Course Schedule", 
        filters={"student_group": enrollment}, 
        fields=["day", "from_time", "to_time", "course", "instructor", "room"], 
        order_by="from_time"
    )
    
    days = {}
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    # Sort by days_order in python instead of SQL FIELD()
    for day in days_order:
        days[day] = [s for s in schedule if s.day == day]
    
    return {"days": days}


@frappe.whitelist()
def get_fee_details(student_id=None):
    """Get fee details for a student"""
    if not student_id:
        student_id = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    
    if not student_id:
        frappe.throw(_("Student not found"))
        
    customer = frappe.db.get_value("Student", student_id, "customer")
    if not customer:
        return {"invoices": [], "total_outstanding": 0}
    
    invoices = frappe.get_all("Sales Invoice", 
        filters={"customer": customer, "docstatus": 1}, 
        fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status"], 
        order_by="posting_date desc", 
        limit=20
    )
    
    return {
        "invoices": invoices,
        "total_outstanding": sum(i.outstanding_amount for i in invoices)
    }
