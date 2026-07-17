import frappe
from frappe import _

@frappe.whitelist()
def get_student_dashboard(student_id=None):
    """Get student dashboard data for mobile/portal"""
    if not student_id:
        student_id = frappe.db.get_value("Custom Student", {"user": frappe.session.user}, "name")
    
    if not student_id:
        frappe.throw(_("Student not found for current user"))
    
    student = frappe.get_doc("Custom Student", student_id)
    
    # Recent attendance (last 30 days)
    attendance = frappe.db.sql("""
        SELECT date, status 
        FROM `tabStudent Attendance` 
        WHERE student = %s 
        ORDER BY date DESC 
        LIMIT 30
    """, student.name, as_dict=True)
    
    present_days = sum(1 for a in attendance if a.status == "Present")
    total_days = len(attendance)
    attendance_pct = round((present_days / total_days) * 100, 1) if total_days > 0 else 0
    
    # Upcoming exams
    upcoming_exams = frappe.db.sql("""
        SELECT es.subject, es.exam_date, es.from_time, es.to_time, es.exam_hall
        FROM `tabExam Schedule` es
        WHERE es.exam_date >= CURDATE()
        ORDER BY es.exam_date ASC
        LIMIT 5
    """, as_dict=True)
    
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
        student = frappe.get_doc("Custom Student", student_id) if frappe.db.exists("Custom Student", student_id) else None
        if not student:
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
        student = frappe.db.get_value("Custom Student", {"user": frappe.session.user}, "name")
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
    schedule = frappe.db.sql("""
        SELECT cs.day, cs.from_time, cs.to_time, cs.course, cs.instructor, cs.room
        FROM `tabCourse Schedule` cs
        WHERE cs.student_group = %s
        ORDER BY FIELD(cs.day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'), cs.from_time
    """, enrollment, as_dict=True)
    
    days = {}
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    for day in days_order:
        days[day] = [s for s in schedule if s.day == day]
    
    return {"days": days}


@frappe.whitelist()
def get_fee_details(student_id=None):
    """Get fee details for a student"""
    if not student_id:
        student_id = frappe.db.get_value("Custom Student", {"user": frappe.session.user}, "name")
    
    if not student_id:
        frappe.throw(_("Student not found"))
    
    invoices = frappe.db.sql("""
        SELECT si.name, si.posting_date, si.due_date, si.grand_total,
               si.outstanding_amount, si.status
        FROM `tabSales Invoice` si
        WHERE si.customer = %s AND si.docstatus = 1
        ORDER BY si.posting_date DESC
        LIMIT 20
    """, student_id, as_dict=True)
    
    return {
        "invoices": invoices,
        "total_outstanding": sum(i.outstanding_amount for i in invoices)
    }
