"""
School Management Software - Demo Data Generator

Usage:
    bench --site [sitename] execute school_management_software.demo.generate
    bench --site [sitename] execute school_management_software.demo.generate \\
        --kwargs '{"verbose": true}'

Dry-run:
    bench --site [sitename] execute school_management_software.demo.generate \\
        --kwargs '{"dry_run": true}'
"""

import frappe
import random
import traceback
from datetime import date, datetime


# ═══════════════════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════════════════


def _safe_create(doctype, kwargs, unique_field=None, ignore_if_exists=True,
                 submit=False, dry_run=False):
    """Create a single record safely. Returns doc name or None if skipped."""
    if dry_run:
        return None

    doc_name = None
    if unique_field and unique_field in kwargs:
        doc_name = kwargs[unique_field]

    if not doc_name:
        meta = frappe.get_meta(doctype, cached=False)
        autoname = meta.autoname or ""
        if autoname.startswith("field:"):
            fn = autoname.replace("field:", "")
            if fn in kwargs:
                doc_name = kwargs[fn]

    if doc_name and ignore_if_exists:
        if frappe.db.exists(doctype, doc_name):
            return None

    try:
        doc = frappe.get_doc({"doctype": doctype, **kwargs})
        doc.insert(ignore_permissions=True, ignore_mandatory=True)
        if submit and doc.meta.is_submittable:
            doc.submit()
        return doc.name
    except Exception as e:
        raise


def _section(label, fn):
    """Run a generator section and return stats."""
    count = 0
    skipped = 0
    errors = []
    try:
        for result in fn():
            if result is None:
                skipped += 1
            else:
                count += 1
    except Exception as e:
        tb = traceback.format_exc()
        errors.append(f"{label}: {e}")
    return {"label": label, "created": count, "skipped": skipped, "errors": errors}


# ═══════════════════════════════════════════════════════════════
# STANDARD MASTER DATA (Education / ERPNext)
# ═══════════════════════════════════════════════════════════════

def aca_academic_year(dry_run):
    for name, start, end in [
        ("2026-2027", date(2026, 4, 1), date(2027, 3, 31)),
    ]:
        yield _safe_create("Academic Year", {
            "academic_year_name": name,
            "year_start_date": start,
            "year_end_date": end,
        }, unique_field="academic_year_name", dry_run=dry_run)


def aca_academic_term(dry_run):
    """Academic Term — standard Education. Requires academic_year."""
    for term_name, s_m, s_d, e_m, e_d in [
        ("Term 1 - 2026-2027", 4, 1, 9, 30),
        ("Term 2 - 2026-2027", 10, 1, 3, 31),
    ]:
        try:
            yield _safe_create("Academic Term", {
                "term_name": term_name,
                "academic_year": "2026-2027",
                "term_start_date": date(2026 if s_m >= 4 else 2027, s_m, s_d),
                "term_end_date": date(2026 if e_m >= 4 else 2027, e_m, e_d),
            }, unique_field="term_name", dry_run=dry_run)
        except Exception as e:
            print(f"  ⚠️ Academic Term '{term_name}': {e}")
            yield None


def aca_program(dry_run):
    grades = ["Jr KG", "Sr KG", "Grade 1", "Grade 2", "Grade 3",
              "Grade 4", "Grade 5", "Grade 6", "Grade 7", "Grade 8",
              "Grade 9", "Grade 10"]
    for g in grades:
        yield _safe_create("Program", {
            "program_name": g,
            "is_graded": 1,
        }, unique_field="program_name", dry_run=dry_run)


def aca_course(dry_run):
    subjects_by_level = {
        "early": ["English", "Mathematics", "Environmental Studies", "Rhymes", "Art & Craft"],
        "primary": ["English", "Mathematics", "Science", "Social Studies", "Hindi",
                    "EVS", "Art & Craft", "Physical Education"],
        "middle": ["English", "Mathematics", "Physics", "Chemistry", "Biology",
                   "History", "Geography", "Civics", "Hindi", "Computer Science",
                   "Physical Education"],
        "high": ["English", "Mathematics", "Physics", "Chemistry", "Biology",
                 "History", "Geography", "Economics", "Computer Science",
                 "Physical Education", "Sanskrit"],
    }
    mapping = {
        "Jr KG": "early", "Sr KG": "early",
        "Grade 1": "primary", "Grade 2": "primary", "Grade 3": "primary",
        "Grade 4": "primary", "Grade 5": "primary",
        "Grade 6": "middle", "Grade 7": "middle", "Grade 8": "middle",
        "Grade 9": "high", "Grade 10": "high",
    }
    for grade, level in mapping.items():
        for subj in subjects_by_level[level]:
            cn = f"{subj} - {grade}"
            yield _safe_create("Course", {"course_name": cn},
                               unique_field="course_name", dry_run=dry_run)


def aca_student_group(dry_run):
    for grade in ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5",
                  "Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10"]:
        for section in ["A", "B"]:
            sg = f"{grade} - Section {section}"
            yield _safe_create("Student Group", {
                "student_group_name": sg,
                "group_based_on": "Batch",
                "program": grade,
                "academic_year": "2026-2027",
            }, unique_field="student_group_name", dry_run=dry_run)


def aca_instructor(dry_run):
    """Instructor — skip department field to avoid missing Department errors."""
    data = [
        "Rajesh Kumar", "Priya Sharma", "Amit Singh", "Sneha Patel",
        "Vikram Reddy", "Anita Desai", "Suresh Verma", "Meera Nair",
        "Ravi Joshi", "Pooja Gupta",
    ]
    for name in data:
        yield _safe_create("Instructor", {
            "instructor_name": name,
            # note: department is a Link to Department doctype;
            # skip it to avoid 'Department not found' errors
        }, unique_field="instructor_name", dry_run=dry_run)


def aca_room(dry_run):
    for wing in ["A", "B"]:
        for floor in range(1, 4):
            for num in range(1, 6):
                rn = f"{wing}{floor}{num:02d}"
                yield _safe_create("Room", {
                    "room_name": rn,
                    "capacity": random.choice([30, 35, 40, 45]),
                }, unique_field="room_name", dry_run=dry_run)


def aca_grading_scale(dry_run):
    """Grading Scale — skip child table (grading intervals) to avoid DB errors."""
    scale = _safe_create("Grading Scale", {
        "grading_scale_name": "Standard A-F Scale",
        "description": "Standard academic grading scale",
    }, unique_field="grading_scale_name", dry_run=dry_run)

    if scale and not dry_run:
        try:
            doc = frappe.get_doc("Grading Scale", scale)
            for code, lo, hi, desc in [
                ("A+", 90, 100, "Outstanding"),
                ("A", 80, 89, "Excellent"),
                ("B+", 70, 79, "Very Good"),
                ("B", 60, 69, "Good"),
                ("C+", 50, 59, "Above Average"),
                ("C", 40, 49, "Average"),
                ("D", 33, 39, "Below Average"),
                ("F", 0, 32, "Fail"),
            ]:
                row = doc.append("intervals", {
                    "grade_code": code,
                    "min_score": lo,
                    "max_score": hi,
                    "grade_description": desc,
                })
            doc.save(ignore_permissions=True)
        except Exception as e:
            print(f"  ⚠️ Grading intervals: {e}")
    yield scale


def aca_fee_category(dry_run):
    for fc in ["Tuition Fee", "Development Fee", "Computer Lab Fee",
               "Library Fee", "Sports Fee", "Transport Fee", "Exam Fee"]:
        yield _safe_create("Fee Category", {"fee_category": fc},
                           unique_field="fee_category", dry_run=dry_run)


def aca_guardian(dry_run):
    data = [
        ("Rajesh Mehta", "rajesh.mehta@email.com", "9876543210"),
        ("Sunita Khan", "sunita.khan@email.com", "9876543211"),
        ("Amit Sharma", "amit.sharma@email.com", "9876543212"),
        ("Priya Gupta", "priya.gupta@email.com", "9876543213"),
        ("Vijay Nair", "vijay.nair@email.com", "9876543214"),
    ]
    for name, email, mobile in data:
        yield _safe_create("Guardian Profile", {
            "guardian_name": name,
            "email_address": email,
            "mobile_number": mobile,
        }, unique_field="guardian_name", dry_run=dry_run)


def aca_student(dry_run):
    data = [
        ("Arjun Mehta", "2008-05-15", "Male", "arjun.mehta@demo.com"),
        ("Sara Khan", "2009-03-22", "Female", "sara.khan@demo.com"),
        ("Rohit Sharma", "2008-11-08", "Male", "rohit.sharma@demo.com"),
        ("Ananya Gupta", "2009-07-14", "Female", "ananya.gupta@demo.com"),
        ("Vivaan Patel", "2008-01-30", "Male", "vivaan.patel@demo.com"),
        ("Ishita Verma", "2009-09-18", "Female", "ishita.verma@demo.com"),
        ("Aditya Singh", "2008-04-25", "Male", "aditya.singh@demo.com"),
        ("Neha Reddy", "2009-12-05", "Female", "neha.reddy@demo.com"),
        ("Karan Joshi", "2008-08-12", "Male", "karan.joshi@demo.com"),
        ("Priya Nair", "2009-02-28", "Female", "priya.nair@demo.com"),
        ("Rahul Kumar", "2007-06-10", "Male", "rahul.kumar@demo.com"),
        ("Divya Desai", "2008-10-20", "Female", "divya.desai@demo.com"),
        ("Manav Agarwal", "2007-03-15", "Male", "manav.agarwal@demo.com"),
        ("Kriti Saxena", "2008-07-08", "Female", "kriti.saxena@demo.com"),
        ("Nikhil Bose", "2007-01-22", "Male", "nikhil.bose@demo.com"),
        ("Aisha Sheikh", "2008-05-30", "Female", "aisha.sheikh@demo.com"),
        ("Harsh Thakur", "2007-09-14", "Male", "harsh.thakur@demo.com"),
        ("Riya Kapoor", "2008-11-25", "Female", "riya.kapoor@demo.com"),
        ("Siddharth Raj", "2007-04-18", "Male", "siddharth.raj@demo.com"),
        ("Tanya Bhatia", "2008-12-02", "Female", "tanya.bhatia@demo.com"),
    ]
    for name, dob, gender, email in data:
        # Split name for first_name so auto-created User works
        parts = name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        yield _safe_create("Student", {
            "student_name": name,
            "student_full_name": name,
            "first_name": first_name,
            "middle_name": "",
            "last_name": last_name,
            "student_email_id": email,
            "title": name,
            "date_of_birth": dob,
            "gender": gender,
        }, unique_field="student_email_id", dry_run=dry_run)


def aca_fee_structure(dry_run):
    if dry_run:
        yield None
        return
    for grade in ["Grade 1", "Grade 5", "Grade 8", "Grade 10"]:
        for fc in ["Tuition Fee", "Development Fee", "Library Fee", "Sports Fee"]:
            fs_name = f"{fc} - {grade} - 2026-2027"
            yield _safe_create("Fee Structure", {
                "fee_structure": fs_name,
                "program": grade,
                "academic_year": "2026-2027",
                "components": [
                    {"fees_category": fc, "amount": random.choice([500, 1000, 1500, 2000])},
                ],
            }, unique_field="fee_structure", dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: HOSTEL
# ═══════════════════════════════════════════════════════════════

def cus_hostel(dry_run):
    for name, htype, addr in [
        ("Boys Hostel - A", "Boys", "Main Campus, Block A"),
        ("Girls Hostel - B", "Girls", "Main Campus, Block B"),
    ]:
        yield _safe_create("Hostel", {
            "hostel_name": name,
            "hostel__type": htype,
            "address": addr,
        }, unique_field="hostel_name", dry_run=dry_run)


def cus_hostel_room_type(dry_run):
    for rt, cap, fee, amenities in [
        ("Single Room", 1, 8000, "Attached bathroom, Study table, Almirah"),
        ("Double Sharing", 2, 5000, "Shared bathroom, Study table"),
        ("Triple Sharing", 3, 3500, "Common area, Shared bathroom"),
    ]:
        yield _safe_create("Hostel Room Types", {
            "room_type": rt,
            "capacity": cap,
            "monthly_fee": fee,
            "amenities": amenities,
        }, unique_field="room_type", dry_run=dry_run)


def cus_warden(dry_run):
    for name, wid, phone in [
        ("Ramesh Gupta", "WAR-001", "9876543301"),
        ("Anita Sharma", "WAR-002", "9876543302"),
    ]:
        yield _safe_create("Warden", {
            "warden_name": name,
            "warden_id": wid,
            "contact_number": phone,
        }, unique_field="warden_name", dry_run=dry_run)


def cus_hostel_block(dry_run):
    hostels = frappe.db.get_all("Hostel", pluck="name") if not dry_run else []
    if dry_run:
        hostels = ["Boys Hostel - A", "Girls Hostel - B"]
    for h in hostels:
        for bl in ["A", "B", "C"]:
            bn = f"{h} - Block {bl}"
            yield _safe_create("Hostel Block", {
                "block_name": bn,
                "hostel": h,
            }, unique_field="block_name", dry_run=dry_run)


def cus_hostel_room(dry_run):
    if dry_run:
        yield None
        return
    hostels = frappe.db.get_all("Hostel", pluck="name")
    room_types = ["1 Sharing AC", "2 Sharing-AC", "3 Sharing-AC", "4 Sharing-AC"]
    statuses = ["Available", "Nearly Full", "Full", "Reserved", "Maintenance"]
    for h in hostels:
        blocks = frappe.db.get_all("Hostel Block", filters={"hostel": h}, pluck="name")
        for floor in range(1, 4):
            for num in range(1, 6):
                rn = f"RM-{h[:3]}-{floor}{num:02d}"
                yield _safe_create("Hostel Room", {
                    "room_number": rn,
                    "hostel": h,
                    "hostel_block": random.choice(blocks) if blocks else "",
                    "floor_number": floor,
                    "room_type": random.choice(room_types),
                    "total_beds": random.choice([1, 2, 3, 4]),
                    "occupied_beds": random.randint(0, 3),
                    "room_status": random.choice(statuses),
                }, unique_field="room_number", dry_run=dry_run)


def cus_mess_menu(dry_run):
    breakfasts = ["Idli Sambar", "Poha", "Upma", "Paratha", "Puri Bhaji", "Dosa", "Sandwich"]
    lunches = ["Dal Rice", "Chapati Curry", "Biryani", "Pulav", "Roti Sabzi", "Noodles", "Khichdi"]
    snacks = ["Samosa", "Biscuits", "Fruits", "Vada Pav", "Popcorn"]
    dinners = ["Chapati Dal", "Rice Sambar", "Fried Rice", "Roti Paneer", "Pasta"]

    for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
        for meal_type, items in [
            ("breakfast", random.choice(breakfasts)),
            ("luch", random.choice(lunches)),
            ("snacks", random.choice(snacks)),
            ("dinner", random.choice(dinners)),
        ]:
            yield _safe_create("Mess Menu", {
                "day": day,
                "meal_type": meal_type,
                "menu_items": items,
                "academic_year": "2026-2027",
            }, dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: TRANSPORT
# ═══════════════════════════════════════════════════════════════

def cus_transport_route(dry_run):
    for name in ["North Route - A", "South Route - B", "East Route - C", "West Route - D"]:
        yield _safe_create("Transport Route", {
            "route_name": name,
            "route_status": "Active",
            "is_active": 1,
        }, unique_field="route_name", dry_run=dry_run)


def cus_transport_vehicle(dry_run):
    data = [
        ("School Bus - Volvo", "KA-01-AB-1234", 50, "Bus", "Active"),
        ("School Bus - Tata", "KA-01-CD-5678", 40, "Bus", "Active"),
        ("Mini Bus - Leyland", "KA-01-EF-9012", 25, "Mini Bus", "Active"),
        ("Transport Van", "KA-01-GH-3456", 15, "Van", "Active"),
    ]
    for vname, reg, cap, vtype, vstat in data:
        yield _safe_create("Transport Vehicle", {
            "vehicle_name": vname,
            "registration_number": reg,
            "capacity": cap,
            "vehicle_type": vtype,
            "vehicle_status": vstat,
        }, unique_field="vehicle_name", dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: LIBRARY
# ═══════════════════════════════════════════════════════════════

def cus_book_author(dry_run):
    authors = ["R.K. Narayan", "Chetan Bhagat", "Amish Tripathi", "Arundhati Roy",
               "Jhumpa Lahiri", "Vikram Seth", "Mulk Raj Anand", "Stephen Hawking",
               "R.S. Aggarwal", "A.P.J. Abdul Kalam"]
    try:
        for name in authors:
            yield _safe_create("Book Author", {
                "naming_series": "AUTH-.YYYY.-",
            }, dry_run=dry_run)
    except Exception as e:
        if "Server Script" in str(e):
            print("  ⚠️ Server Scripts disabled - Book Authors use naming_series")
        yield None


def cus_book_category(dry_run):
    for cat in ["Fiction", "Non-Fiction", "Science", "Mathematics", "History",
                "Literature", "Reference", "Children", "Competitive Exams"]:
        yield _safe_create("Book Category", {"category_name": cat},
                           unique_field="category_name", dry_run=dry_run)


def cus_library_rack(dry_run):
    for rack in ["Rack A1", "Rack A2", "Rack B1", "Rack B2", "Rack C1"]:
        yield _safe_create("Library Rack", {"rack_name": rack},
                           unique_field="rack_name", dry_run=dry_run)


def cus_library_book(dry_run):
    if dry_run:
        yield None
        return
    authors = frappe.db.get_all("Book Author", pluck="name", limit=8)
    categories = frappe.db.get_all("Book Category", pluck="name")
    racks = frappe.db.get_all("Library Rack", pluck="name")

    books = [
        ("9780140189849", "Fiction", "Penguin", 1950),
        ("9781416562603", "Fiction", "Harper Collins", 2008),
        ("9789380658458", "Fiction", "Rupa Publications", 2010),
        ("9780006550688", "Fiction", "Penguin", 1997),
        ("9780618101367", "Fiction", "Harper Collins", 1999),
        ("9780553380163", "Science", "Bantam", 1988),
        ("9788177097575", "Mathematics", "R.S. Aggarwal", 2020),
        ("9780195687859", "History", "Oxford Press", 2005),
        ("9788173711466", "Non-Fiction", "Universities Press", 1999),
        ("9780143031031", "History", "Penguin", 1946),
    ]
    for isbn, cat, pub, year in books:
        author = random.choice(authors) if authors else ""
        category = cat if cat in categories else (categories[0] if categories else "")
        rack = random.choice(racks) if racks else ""
        yield _safe_create("Library Book", {
            "isbn": isbn,
            "author": author,
            "category": category,
            "publisher": pub,
            "publication_year": year,
            "language": "English",
            "status": "Available",
            "rack_location": rack,
        }, dry_run=dry_run)


def cus_book_copy(dry_run):
    if dry_run:
        yield None
        return
    books = frappe.db.get_all("Library Book", pluck="name", limit=8)
    racks = frappe.db.get_all("Library Rack", pluck="name")
    for bk in books:
        for i in range(random.randint(1, 3)):
            yield _safe_create("Book Copy", {
                "isbn": bk,
                "copy_number": f"CP-{bk}-{i+1}",
                "rack": random.choice(racks) if racks else "",
                "condition": "Good",
                "copy_status": "Available",
                "price": random.randint(200, 800),
            }, dry_run=dry_run)


def cus_library_member(dry_run):
    if dry_run:
        yield None
        return
    students = frappe.db.get_all("Student", pluck="name", limit=10)
    for i, stu in enumerate(students):
        mid = f"LIB-MEM-{i+1:04d}"
        yield _safe_create("Library Member", {
            "member_id": mid,
            "member_type": "Student",
            "student": stu,
            "member_name": stu,
            "academic_year": "2026-2027",
            "membership_start": date(2026, 4, 1),
            "membership_end": date(2027, 3, 31),
            "membership_status": "Active",
            "max_books_allowed": 3,
        }, unique_field="member_id", dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: EXAM
# ═══════════════════════════════════════════════════════════════

def cus_exam_term(dry_run):
    for name, frm, to in [
        ("Term 1 - 2026-2027", date(2026, 7, 1), date(2026, 9, 30)),
        ("Term 2 - 2026-2027", date(2026, 12, 1), date(2027, 2, 28)),
    ]:
        yield _safe_create("Exam Term", {
            "term_name": name,
            "academic_year": "2026-2027",
            "from_date": frm,
            "to_date": to,
            "is_active": 1,
        }, unique_field="term_name", dry_run=dry_run)


def cus_exam_hall(dry_run):
    """Exam Hall — autoname: field:hall_number (NOT hall_name)."""
    for hall_num, cap in [
        ("HALL-001", 120),
        ("HALL-002", 60),
        ("HALL-003", 60),
    ]:
        yield _safe_create("Exam Hall", {
            "hall_number": hall_num,
            "capacity": cap,
            "status": "Available",
        }, unique_field="hall_number", dry_run=dry_run)


def cus_event_type(dry_run):
    for name in ["Assembly", "Sports Day", "Cultural Event", "PTA Meeting",
                 "Science Fair", "Field Trip", "Workshop"]:
        yield _safe_create("Event Type", {
            "event_type_name": name,
        }, unique_field="event_type_name", dry_run=dry_run)


def cus_school_event(dry_run):
    events = [
        ("Annual Day Celebration", "Assembly", date(2026, 12, 15), date(2026, 12, 15),
         "Main Auditorium", "Upcoming"),
        ("Sports Day", "Sports Day", date(2026, 11, 20), date(2026, 11, 22),
         "School Ground", "Upcoming"),
        ("Science Fair", "Science Fair", date(2026, 10, 5), date(2026, 10, 5),
         "Science Lab Block", "Upcoming"),
    ]
    for title, etype, sd, ed, venue, status in events:
        yield _safe_create("School Event", {
            "title": title,
            "event_type": etype,
            "start_date": sd,
            "end_date": ed,
            "venue": venue,
            "status": status,
            "audience": "Everybody",
            "academic_year": "2026-2027",
        }, dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: AI & GAMIFICATION
# ═══════════════════════════════════════════════════════════════

def cus_ai_settings(dry_run):
    if dry_run:
        yield None
        return
    if not frappe.db.exists("AI Settings", "AI Configuration"):
        try:
            doc = frappe.get_single("AI Settings")
            doc.update({
                "setting_name": "AI Configuration",
                "enable_ai": 1,
                "provider": "OpenAI",
                "model": "gpt-4o-mini",
                "max_tokens": 2000,
                "temperature": 0.7,
                "enable_chatbot": 1,
                "enable_grading": 1,
                "enable_content_generation": 1,
                "enable_report_card_remarks": 1,
                "daily_request_limit": 1000,
            })
            doc.save(ignore_permissions=True)
            yield doc.name
        except Exception as e:
            print(f"  ⚠️ AI Settings: {e}")
            yield None
    else:
        yield None


def cus_gamification_settings(dry_run):
    if dry_run:
        yield None
        return
    if not frappe.db.exists("Gamification Settings", "Gamification Settings"):
        try:
            doc = frappe.get_single("Gamification Settings")
            doc.update({
                "enable_points": 1,
                "enable_badges": 1,
                "enable_leaderboard": 1,
                "enable_streaks": 1,
                "attendance_point": 10,
                "homework_completion_point": 20,
                "exam_performance_point": 50,
                "extra_curricular_point": 30,
                "behaviour_point": 15,
                "streak_bonus_multiplier": 1.5,
                "leaderboard_refresh_frequency": "Weekly",
                "max_leaderboard_entries": 50,
            })
            doc.save(ignore_permissions=True)
            yield doc.name
        except Exception:
            yield None
    else:
        yield None


def cus_badge(dry_run):
    for name, cat, ctype, pts in [
        ("Perfect Attendance", "Attendance", "Points Threshold", 100),
        ("Star Student", "Academic", "Points Threshold", 200),
        ("Homework Hero", "Academic", "Points Threshold", 150),
        ("Sports Champion", "Sports", "Achievement Based", 0),
        ("Kindness Badge", "Behaviour", "Manual Award", 0),
    ]:
        yield _safe_create("Badge Definition", {
            "badge_name": name,
            "category": cat,
            "criteria_type": ctype,
            "points_required": pts if ctype == "Points Threshold" else 0,
            "badge_color": random.choice(["#FFD700", "#C0C0C0", "#CD7F32"]),
            "is_active": 1,
        }, unique_field="badge_name", dry_run=dry_run)


def cus_points_ledger(dry_run):
    if dry_run:
        yield None
        return
    students = frappe.db.get_all("Student", pluck="name", limit=5)
    for stu in students:
        yield _safe_create("Student Points Ledger", {
            "student": stu,
            "points": random.randint(50, 500),
            "reason": "Demo data initialization",
            "date": date(2026, 4, 1),
        }, dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: GOVERNANCE & COMPLIANCE
# ═══════════════════════════════════════════════════════════════

def gov_committee(dry_run):
    for name, ctype in [
        ("Academic Committee", "Academic Council"),
        ("Finance Committee", "Finance Committee"),
        ("Disciplinary Committee", "Disciplinary Committee"),
        ("Sports Committee", "Sports Committee"),
    ]:
        yield _safe_create("Committee Definition", {
            "committee_name": name,
            "committee_type": ctype,
            "purpose": f"Oversee {name.lower()} matters.",
        }, unique_field="committee_name", dry_run=dry_run)


def gov_board_meeting(dry_run):
    for title, mtype in [
        ("Annual Board Meeting - 2026", "Board Meeting"),
        ("Academic Committee Review", "Committee Meeting"),
        ("Finance Committee Meeting", "Executive Meeting"),
    ]:
        yield _safe_create("Board Meeting", {
            "naming_series": "BMEET-.YYYY.-",
            "title": title,
            "meeting_type": mtype,
            "date": date(2026, random.randint(1, 6), random.randint(1, 28)),
            "time": "10:00:00",
            "venue": "Conference Room",
            "meeting_status": "Scheduled",
        }, dry_run=dry_run)


def gov_compliance(dry_run):
    for name, stype, body in [
        ("ISO 27001:2022", "ISO 27001", "TUV Rheinland"),
        ("GDPR Readiness", "GDPR", "Data Protection Office"),
        ("FERPA Compliance", "FERPA", "Education Department"),
    ]:
        yield _safe_create("Compliance Certification", {
            "certification_name": name,
            "standard_type": stype,
            "certifying_body": body,
            "issue_date": date(2025, 1, 1),
            "expiry_date": date(2028, 1, 1),
            "status": "Active",
            "is_compliant": 1,
        }, unique_field="certification_name", submit=True, dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: ASSETS
# ═══════════════════════════════════════════════════════════════

def ast_asset_register(dry_run):
    for name, code, cat, cost in [
        ("Smart Board - Class A1", "AST-001", "Electronics", 50000),
        ("Computer Lab Desktops", "AST-002", "IT Equipment", 250000),
        ("Library Books Collection", "AST-003", "Library", 100000),
        ("Science Lab Equipment", "AST-004", "Laboratory Equipment", 150000),
        ("School Bus - Volvo", "AST-005", "Transport Vehicle", 3500000),
    ]:
        yield _safe_create("Asset Register", {
            "asset_name": name,
            "asset_code": code,
            "category": cat,
            "purchase_date": date(2025, random.randint(1, 12), random.randint(1, 28)),
            "purchase_cost": cost,
            "current_value": cost,
            "condition": "Good",
            "status": "In Service",
        }, unique_field="asset_code", submit=True, dry_run=dry_run)


def ast_asset_maintenance(dry_run):
    if dry_run:
        yield None
        return
    assets = frappe.db.get_all("Asset Register", pluck="name", limit=3)
    for i, asset in enumerate(assets):
        mid = f"MAINT-{i+1:04d}"
        yield _safe_create("Asset Maintenance", {
            "maintenance_id": mid,
            "asset_code": asset,
            "maintenance_type": "Preventive",
            "issue_description": "Regular maintenance check.",
            "maintenance_date": date(2026, random.randint(1, 6), random.randint(1, 28)),
            "status": "Completed",
        }, unique_field="maintenance_id", submit=True, dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: BIOMETRIC
# ═══════════════════════════════════════════════════════════════

def cus_biometric(dry_run):
    for name, dtype, location in [
        ("Main Gate Biometric", "Fingerprint", "Main Entrance"),
        ("Staff Room Biometric", "Face Recognition", "Staff Room"),
        ("Library Entry RFID", "RFID", "Library Entrance"),
    ]:
        yield _safe_create("Biometric Device", {
            "device_name": name,
            "device_type": dtype,
            "location": location,
            "ip_address": f"192.168.1.{random.randint(10, 100)}",
            "port": 8080,
            "is_active": 1,
        }, unique_field="device_name", dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: ALUMNI
# ═══════════════════════════════════════════════════════════════

def cus_alumni(dry_run):
    for i, (name, year, occ, org) in enumerate([
        ("Rahul Verma", 2020, "Software Engineer", "Tech Corp"),
        ("Priya Patel", 2019, "Doctor", "City Hospital"),
        ("Amit Kumar", 2021, "Business Analyst", "Finance Ltd"),
        ("Sneha Reddy", 2020, "Teacher", "Public School"),
    ]):
        aid = f"ALUM-{i+1:04d}"
        yield _safe_create("Alumni Record", {
            "alumni_id": aid,
            "student_name": name,
            "graduation_year": year,
            "current_occupation": occ,
            "current_organization": org,
            "contact_number": f"9{random.randint(100000000, 999999999)}",
            "alumni_status": "Active",
        }, unique_field="alumni_id", dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: LMS / QUESTION BANK
# ═══════════════════════════════════════════════════════════════

def cus_question_bank(dry_run):
    if dry_run:
        yield None
        return
    courses = frappe.db.get_all("Course", pluck="name", limit=10)
    questions = [
        ("What is the capital of France?", "Multiple Choice", 2),
        ("What is 5 + 7?", "Short Answer", 1),
        ("The Earth revolves around the Sun.", "True/False", 1),
        ("Explain photosynthesis", "Long Answer", 5),
        ("Which planet is known as Red Planet?", "Single Choice", 2),
    ]
    for q_title, q_type, marks in questions:
        course = random.choice(courses) if courses else ""
        yield _safe_create("Question Bank", {
            "question_title": q_title,
            "question_type": q_type,
            "question_text": f"<p>{q_title}</p>",
            "subject": course,
            "marks": marks,
            "difficulty_level": random.choice(["Easy", "Medium", "Hard"]),
        }, unique_field="question_title", dry_run=dry_run)


def cus_course_module(dry_run):
    if dry_run:
        yield None
        return
    courses = frappe.db.get_all("Course", pluck="name", limit=6)
    for i, title in enumerate([
        "Introduction to Algebra",
        "Basic Chemistry Concepts",
        "English Grammar Fundamentals",
        "World History Overview",
    ]):
        course = courses[i % len(courses)] if courses else ""
        yield _safe_create("Course Module", {
            "module_title": title,
            "course": course,
            "module_number": i + 1,
            "description": f"Demo module covering {title}",
        }, unique_field="module_title", dry_run=dry_run)


def cus_assignment(dry_run):
    if dry_run:
        yield None
        return
    courses = frappe.db.get_all("Course", pluck="name", limit=4)
    for i, title in enumerate([
        "Mathematics Homework - Week 1",
        "Science Lab Report",
        "English Essay Assignment",
        "History Project",
    ]):
        course = courses[i % len(courses)] if courses else ""
        yield _safe_create("Assignment", {
            "assignment_title": title,
            "course": course,
            "description": f"Complete the {title}.",
            "due_date": date(2026, 5, 15 + i * 7),
            "max_score": 100,
        }, unique_field="assignment_title", submit=True, dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: FRONT OFFICE
# ═══════════════════════════════════════════════════════════════

def fro_visitor_log(dry_run):
    for name, phone, visit_to, purpose, status in [
        ("Rahul's Father", "9876543401", "Principal", "Parent Meeting", "Checked In"),
        ("Book Supplier", "9876543402", "Admin Office", "Book Delivery", "Checked Out"),
        ("Sports Coach", "9876543403", "Sports Dept", "Coaching Session", "Checked Out"),
    ]:
        yield _safe_create("Visitor Log", {
            "visitor_name": name,
            "contact_number": phone,
            "visiting_to": visit_to,
            "purpose": purpose,
            "in_time": datetime(2026, 4, random.randint(1, 15), random.randint(8, 16), 0),
            "status": status,
        }, dry_run=dry_run)


def fro_call_log(dry_run):
    for caller, phone, ctype, purpose in [
        ("Parent - Arjun Mehta", "9876543220", "Incoming", "Fee Inquiry"),
        ("Vendor - Stationery", "9876543405", "Incoming", "Supply Order"),
        ("Transport Dept", "9876543406", "Outgoing", "Bus Route Confirmation"),
    ]:
        yield _safe_create("Call Log", {
            "caller_name": caller,
            "contact_number": phone,
            "call_type": ctype,
            "purpose": purpose,
            "call_date": date(2026, 4, random.randint(1, 15)),
        }, dry_run=dry_run)


def fro_postal_record(dry_run):
    for ptype, sender, subject in [
        ("Incoming", "Education Board", "Exam Results Notification"),
        ("Outgoing", "Parent Association", "PTM Invitation"),
        ("Confidential", "Management", "Board Meeting Minutes"),
    ]:
        yield _safe_create("Postal Record", {
            "postal_type": ptype,
            "sender_recipient": sender,
            "subject": subject,
            "date": date(2026, 4, random.randint(1, 15)),
        }, dry_run=dry_run)


def fro_admission_enquiry(dry_run):
    for i, (name, phone, program) in enumerate([
        ("New Parent 1", "9876543410", "Grade 1"),
        ("New Parent 2", "9876543411", "Grade 6"),
        ("New Parent 3", "9876543412", "Jr KG"),
    ]):
        eid = f"ENQ-{i+1:04d}"
        yield _safe_create("Admission Enquiry", {
            "enquiry_id": eid,
            "student_name": name,
            "contact_number": phone,
            "program": program,
            "academic_year": "2026-2027",
            "reference_source": "Website",
            "status": "New",
        }, unique_field="enquiry_id", dry_run=dry_run)


def fro_response_template(dry_run):
    for name, ctype, msg in [
        ("Fee Reminder", "Fee", "Dear Parent, kindly pay the pending fee."),
        ("Attendance Alert", "Attendance",
         "Your ward was absent on {date}. Kindly send a leave note."),
        ("Event Notification", "Event",
         "Dear Parent, {event_name} is scheduled on {date}."),
    ]:
        yield _safe_create("Response Template", {
            "template_name": name,
            "type": ctype,
            "message": msg,
        }, unique_field="template_name", dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: CERTIFICATES
# ═══════════════════════════════════════════════════════════════

def cus_certificate_template(dry_run):
    """Certificate Template — field: certificate_name (NOT template_name)."""
    try:
        yield _safe_create("Certificate Template", {
            "certificate_name": "Bonafide Certificate",
            "applicable_for": "Student",
            "print_format": "Student Certificate Print",
            "is_active": 1,
        }, unique_field="certificate_name", dry_run=dry_run)
    except Exception as e:
        print(f"  ⚠️ Certificate Template: {e}")
        yield None


def cus_student_certificate(dry_run):
    if dry_run:
        yield None
        return
    students = frappe.db.get_all("Student", pluck="name", limit=5)
    if not frappe.db.exists("Certificate Template", "Bonafide Certificate"):
        print("  ⚠️ Certificate Template missing — skipping student certificates")
        yield None
        return
    for stu in students:
        yield _safe_create("Student Certificate", {
            "naming_series": "SCRT-.YYYY.-",
            "student": stu,
            "template": "Bonafide Certificate",
        }, dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: GRIEVANCE
# ═══════════════════════════════════════════════════════════════

def cus_grievance(dry_run):
    """Grievance Box — category must be one of: Electrical, Plumbing,
    Furniture, Mess, Cleaning, Internet, Other (NOT 'Maintenance')."""
    for desc, cat, priority in [
        ("Room A/C not working", "Electrical", "High"),
        ("Mess food quality issue", "Mess", "Medium"),
        ("Broken window in Room 102", "Plumbing", "Low"),
    ]:
        yield _safe_create("Grievance Box", {
            "description": desc,
            "complaint_type": "Maintenance",
            "category": cat,
            "priority": priority,
            "complaint_date": date(2026, 4, random.randint(1, 10)),
            "status": "Open",
        }, dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: TRANSPORT OPERATIONS
# ═══════════════════════════════════════════════════════════════

def cus_transport_assignment(dry_run):
    if dry_run:
        yield None
        return
    routes = frappe.db.get_all("Transport Route", pluck="name", limit=2)
    for name in ["Arjun Mehta", "Sara Khan", "Rohit Sharma"]:
        route = random.choice(routes) if routes else ""
        yield _safe_create("Student Transport Assignment", {
            "student_name": name,
            "transport_route": route,
            "transport_mode": "School Bus",
            "is_active": 1,
            "assigned_date": date(2026, 4, 1),
        }, submit=True, dry_run=dry_run)


def cus_gps_log(dry_run):
    if dry_run:
        yield None
        return
    vehicles = frappe.db.get_all("Transport Vehicle", pluck="name", limit=2)
    for v in vehicles:
        for _ in range(3):
            yield _safe_create("Vehicle GPS Tracking Log", {
                "vehicle": v,
                "latitude": f"12.{random.randint(900000, 999999)}",
                "longitude": f"77.{random.randint(500000, 599999)}",
                "timestamp": datetime(2026, 4, random.randint(1, 5),
                                       random.randint(7, 9), random.randint(0, 59)),
                "speed_kmh": random.randint(20, 60),
            }, dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM: FEES
# ═══════════════════════════════════════════════════════════════

def cus_fee_installment(dry_run):
    for cat, amt in [
        ("Tuition Fee", 2500),
        ("Development Fee", 1000),
        ("Library Fee", 300),
        ("Sports Fee", 200),
    ]:
        yield _safe_create("Student Fee Installment", {
            "fee_category": cat,
            "due_date": random.choice([date(2026, 5, 15), date(2026, 8, 15)]),
            "amount": amt,
            "status": "Pending",
            "outstanding_amount": amt,
        }, dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def generate(dry_run=False, verbose=True):
    """Generate all demo data."""
    print("=" * 60)
    print("SCHOOL MANAGEMENT SOFTWARE - DEMO DATA GENERATOR")
    if dry_run:
        print("  *** DRY RUN MODE ***")
    print("=" * 60)

    sections = [
        ("Academic Year", lambda: aca_academic_year(dry_run)),
        ("Academic Term", lambda: aca_academic_term(dry_run)),
        ("Program", lambda: aca_program(dry_run)),
        ("Course", lambda: aca_course(dry_run)),
        ("Student Group", lambda: aca_student_group(dry_run)),
        ("Instructor", lambda: aca_instructor(dry_run)),
        ("Room", lambda: aca_room(dry_run)),
        ("Grading Scale", lambda: aca_grading_scale(dry_run)),
        ("Fee Category", lambda: aca_fee_category(dry_run)),
        ("Guardian Profile", lambda: aca_guardian(dry_run)),
        ("Student", lambda: aca_student(dry_run)),
        ("Fee Structure", lambda: aca_fee_structure(dry_run)),
        ("Hostel", lambda: cus_hostel(dry_run)),
        ("Hostel Room Types", lambda: cus_hostel_room_type(dry_run)),
        ("Warden", lambda: cus_warden(dry_run)),
        ("Hostel Block", lambda: cus_hostel_block(dry_run)),
        ("Hostel Room", lambda: cus_hostel_room(dry_run)),
        ("Mess Menu", lambda: cus_mess_menu(dry_run)),
        ("Transport Route", lambda: cus_transport_route(dry_run)),
        ("Transport Vehicle", lambda: cus_transport_vehicle(dry_run)),
        ("Book Author", lambda: cus_book_author(dry_run)),
        ("Book Category", lambda: cus_book_category(dry_run)),
        ("Library Rack", lambda: cus_library_rack(dry_run)),
        ("Library Book", lambda: cus_library_book(dry_run)),
        ("Book Copy", lambda: cus_book_copy(dry_run)),
        ("Library Member", lambda: cus_library_member(dry_run)),
        ("Exam Term", lambda: cus_exam_term(dry_run)),
        ("Exam Hall", lambda: cus_exam_hall(dry_run)),
        ("Event Type", lambda: cus_event_type(dry_run)),
        ("School Event", lambda: cus_school_event(dry_run)),
        ("AI Settings", lambda: cus_ai_settings(dry_run)),
        ("Gamification Settings", lambda: cus_gamification_settings(dry_run)),
        ("Badge Definition", lambda: cus_badge(dry_run)),
        ("Student Points Ledger", lambda: cus_points_ledger(dry_run)),
        ("Committee Definition", lambda: gov_committee(dry_run)),
        ("Board Meeting", lambda: gov_board_meeting(dry_run)),
        ("Compliance Certification", lambda: gov_compliance(dry_run)),
        ("Asset Register", lambda: ast_asset_register(dry_run)),
        ("Asset Maintenance", lambda: ast_asset_maintenance(dry_run)),
        ("Biometric Device", lambda: cus_biometric(dry_run)),
        ("Alumni Record", lambda: cus_alumni(dry_run)),
        ("Question Bank", lambda: cus_question_bank(dry_run)),
        ("Course Module", lambda: cus_course_module(dry_run)),
        ("Assignment", lambda: cus_assignment(dry_run)),
        ("Visitor Log", lambda: fro_visitor_log(dry_run)),
        ("Call Log", lambda: fro_call_log(dry_run)),
        ("Postal Record", lambda: fro_postal_record(dry_run)),
        ("Admission Enquiry", lambda: fro_admission_enquiry(dry_run)),
        ("Response Template", lambda: fro_response_template(dry_run)),
        ("Grievance Box", lambda: cus_grievance(dry_run)),
        ("Certificate Template", lambda: cus_certificate_template(dry_run)),
        ("Student Certificate", lambda: cus_student_certificate(dry_run)),
        ("Transport Assignment", lambda: cus_transport_assignment(dry_run)),
        ("GPS Tracking Log", lambda: cus_gps_log(dry_run)),
        ("Fee Installment", lambda: cus_fee_installment(dry_run)),
    ]

    results = []
    for label, fn in sections:
        r = _section(label, fn)
        results.append(r)
        frappe.db.commit()
        if verbose:
            status = f"✅ {r['created']} created"
            if r['skipped']:
                status += f", {r['skipped']} skipped"
            if r['errors']:
                status += f", ❌ {len(r['errors'])} errors"
            print(f"  {label:35s} {status}")

    # Report
    total_created = sum(r['created'] for r in results)
    total_skipped = sum(r['skipped'] for r in results)
    all_errors = [e for r in results for e in r['errors']]

    print("\n" + "=" * 60)
    print("DEMO DATA GENERATION REPORT")
    print("=" * 60)
    for r in results:
        status = f"✅ {r['created']} created"
        if r['skipped']:
            status += f", {r['skipped']} skipped"
        if r['errors']:
            status += f", ❌ {len(r['errors'])} errors"
        print(f"  {r['label']:35s} {status}")

    print("-" * 60)
    print(f"  TOTAL: {total_created} created, {total_skipped} skipped")
    if all_errors:
        print(f"  ERRORS: {len(all_errors)}")
        for e in all_errors:
            print(f"    ⚠️  {e}")
    print("=" * 60)

    if not dry_run:
        print("\n💡 Done! Run 'bench clear-cache' if records don't appear immediately.")
    else:
        print("\n💡 Dry-run complete. No data was inserted.")

    return results


if __name__ == "__main__":
    generate()
