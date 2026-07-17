"""
School Management Software - Demo Data Generator

Generates comprehensive demo data for ALL custom doctypes in this app
plus essential standard ERPNext/Education doctypes.

Usage:
    bench --site [sitename] execute school_management_software.demo.generate
    bench --site [sitename] execute school_management_software.demo.generate --kwargs '{"verbose": true}'

Dry-run mode (no inserts, just validates):
    bench --site [sitename] execute school_management_software.demo.generate --kwargs '{"dry_run": true}'
"""

import frappe
import random
from datetime import date, datetime, timedelta


# ═══════════════════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════════════════

def _safe_create(doctype, kwargs, unique_field=None, ignore_if_exists=True,
                 submit=False, dry_run=False):
    """Create a single record safely.

    - Checks if record exists (by unique_field or computed name).
    - Handles different naming rules.
    - Optionally submits submittable doctypes.
    """
    if dry_run:
        return f"[DRY-RUN] Would create {doctype}: {kwargs}"

    # Determine the name for existence check
    doc_name = None
    if unique_field and unique_field in kwargs:
        doc_name = kwargs[unique_field]

    if doc_name and ignore_if_exists:
        if frappe.db.exists(doctype, doc_name):
            return None  # already exists

    # If unique_field not given, try to detect from autoname pattern
    if not doc_name:
        # Fetch the DocType meta
        meta = frappe.get_meta(doctype, cached=False)
        autoname = meta.autoname or ""
        if autoname.startswith("field:"):
            fn = autoname.replace("field:", "")
            if fn in kwargs:
                doc_name = kwargs[fn]
                if doc_name and frappe.db.exists(doctype, doc_name):
                    return None

    try:
        doc = frappe.get_doc({"doctype": doctype, **kwargs})
        doc.insert(ignore_permissions=True, ignore_mandatory=True)

        if submit and doc.meta.get("is_submittable"):
            doc.submit()

        return doc.name
    except Exception as e:
        raise


def _exec(label, fn, verbose=False):
    """Execute a section and capture stats."""
    errors = []
    count = 0
    skipped = 0
    try:
        for result in fn():
            if result is None:
                skipped += 1
            else:
                count += 1
    except Exception as e:
        errors.append(f"{label}: {e}")

    return {"label": label, "created": count, "skipped": skipped, "errors": errors}


def _report(results, verbose=False):
    """Print summary."""
    print("=" * 60)
    print("DEMO DATA GENERATION REPORT")
    print("=" * 60)
    total_created = 0
    total_skipped = 0
    total_errors = []
    for r in results:
        status = f"✅ {r['created']} created"
        if r['skipped']:
            status += f", {r['skipped']} skipped"
        if r['errors']:
            status += f", ❌ {len(r['errors'])} errors"
            total_errors.extend(r['errors'])
        print(f"  {r['label']:40s} {status}")
        total_created += r['created']
        total_skipped += r['skipped']

    print("-" * 60)
    print(f"  TOTAL: {total_created} created, {total_skipped} skipped")
    if total_errors:
        print(f"  ERRORS: {len(total_errors)}")
        for e in total_errors:
            print(f"    ⚠️  {e}")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════
# MASTER DATA GENERATORS
# ═══════════════════════════════════════════════════════════════

def _create_academic_years(dry_run=False):
    """Academic Year (standard Education)"""
    for name, start, end in [
        ("2026-2027", date(2026, 4, 1), date(2027, 3, 31)),
    ]:
        yield _safe_create("Academic Year", {
            "academic_year_name": name,
            "year_start_date": start,
            "year_end_date": end,
        }, unique_field="academic_year_name", dry_run=dry_run)


def _create_academic_terms(dry_run=False):
    """Academic Term (standard Education)"""
    for term_name, s_m, s_d, e_m, e_d in [
        ("Term 1", 4, 1, 9, 30),
        ("Term 2", 10, 1, 3, 31),
    ]:
        yield _safe_create("Academic Term", {
            "term_name": term_name,
            "term_start_date": date(2026 if s_m >= 4 else 2027, s_m, s_d),
            "term_end_date": date(2026 if e_m >= 4 else 2027, e_m, e_d),
        }, unique_field="term_name", dry_run=dry_run)


def _create_programs(dry_run=False):
    """Program / Grades (standard Education)"""
    grades = ["Jr KG", "Sr KG", "Grade 1", "Grade 2", "Grade 3",
              "Grade 4", "Grade 5", "Grade 6", "Grade 7", "Grade 8",
              "Grade 9", "Grade 10"]
    for g in grades:
        yield _safe_create("Program", {
            "program_name": g,
            "is_graded": 1,
        }, unique_field="program_name", dry_run=dry_run)


def _create_courses(dry_run=False):
    """Courses / Subjects (standard Education)"""
    subjects_by_level = {
        "early": ["English", "Mathematics", "Environmental Studies", "Rhymes", "Art & Craft"],
        "primary": ["English", "Mathematics", "Science", "Social Studies", "Hindi",
                    "Environmental Studies", "Art & Craft", "Physical Education"],
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
        subjects = subjects_by_level[level]
        for subj in subjects:
            cn = f"{subj} - {grade}"
            yield _safe_create("Course", {
                "course_name": cn,
            }, unique_field="course_name", dry_run=dry_run)


def _create_student_groups(dry_run=False):
    """Student Groups / Sections (standard Education)"""
    for grade in ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5",
                  "Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10"]:
        for section in ["A", "B"]:
            sg_name = f"{grade} - Section {section}"
            yield _safe_create("Student Group", {
                "student_group_name": sg_name,
                "group_based_on": "Batch",
                "program": grade,
                "academic_year": "2026-2027",
            }, unique_field="student_group_name", dry_run=dry_run)


def _create_instructors(dry_run=False):
    """Instructors (standard Education)"""
    data = [
        ("EMP001", "Rajesh Kumar", "Mathematics"),
        ("EMP002", "Priya Sharma", "Science"),
        ("EMP003", "Amit Singh", "English"),
        ("EMP004", "Sneha Patel", "Hindi"),
        ("EMP005", "Vikram Reddy", "Physics"),
        ("EMP006", "Anita Desai", "Chemistry"),
        ("EMP007", "Suresh Verma", "Biology"),
        ("EMP008", "Meera Nair", "History"),
        ("EMP009", "Ravi Joshi", "Computer Science"),
        ("EMP010", "Pooja Gupta", "Physical Education"),
    ]
    for emp_id, name, dept in data:
        yield _safe_create("Instructor", {
            "instructor_name": name,
            "employee": emp_id,
            "department": dept,
        }, unique_field="instructor_name", dry_run=dry_run)


def _create_rooms(dry_run=False):
    """Rooms / Classrooms (standard Education)"""
    for wing in ["A", "B"]:
        for floor in range(1, 4):
            for num in range(1, 6):
                rn = f"{wing}{floor}{num:02d}"
                yield _safe_create("Room", {
                    "room_name": rn,
                    "capacity": random.choice([30, 35, 40, 45]),
                }, unique_field="room_name", dry_run=dry_run)


def _create_grading_scale(dry_run=False):
    """Grading Scale (standard Education) with intervals."""
    scale = _safe_create("Grading Scale", {
        "grading_scale_name": "Standard A-F Scale",
        "description": "Standard academic grading scale",
    }, unique_field="grading_scale_name", dry_run=dry_run)
    if scale and not dry_run:
        for code, lo, hi in [
            ("A+", 90, 100), ("A", 80, 89), ("B+", 70, 79),
            ("B", 60, 69), ("C+", 50, 59), ("C", 40, 49),
            ("D", 33, 39), ("F", 0, 32),
        ]:
            key = {"parent": scale, "grade_code": code}
            if not frappe.db.exists("Grading Structure", key):
                doc = frappe.get_doc({
                    "doctype": "Grading Structure",
                    "parent": scale,
                    "parenttype": "Grading Scale",
                    "parentfield": "intervals",
                    "grade_code": code,
                    "min_score": lo,
                    "max_score": hi,
                })
                doc.insert(ignore_permissions=True)
    yield scale


def _create_guardians(dry_run=False):
    """Guardian Profile (custom)"""
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


# ═══════════════════════════════════════════════════════════════
# STUDENTS
# ═══════════════════════════════════════════════════════════════

def _create_students(dry_run=False):
    """Students (standard Education)"""
    data = [
        ("Arjun Mehta", "2008-05-15", "Male", "arjun.mehta@demo.com", "9876543220"),
        ("Sara Khan", "2009-03-22", "Female", "sara.khan@demo.com", "9876543221"),
        ("Rohit Sharma", "2008-11-08", "Male", "rohit.sharma@demo.com", "9876543222"),
        ("Ananya Gupta", "2009-07-14", "Female", "ananya.gupta@demo.com", "9876543223"),
        ("Vivaan Patel", "2008-01-30", "Male", "vivaan.patel@demo.com", "9876543224"),
        ("Ishita Verma", "2009-09-18", "Female", "ishita.verma@demo.com", "9876543225"),
        ("Aditya Singh", "2008-04-25", "Male", "aditya.singh@demo.com", "9876543226"),
        ("Neha Reddy", "2009-12-05", "Female", "neha.reddy@demo.com", "9876543227"),
        ("Karan Joshi", "2008-08-12", "Male", "karan.joshi@demo.com", "9876543228"),
        ("Priya Nair", "2009-02-28", "Female", "priya.nair@demo.com", "9876543229"),
        ("Rahul Kumar", "2007-06-10", "Male", "rahul.kumar@demo.com", "9876543230"),
        ("Divya Desai", "2008-10-20", "Female", "divya.desai@demo.com", "9876543231"),
        ("Manav Agarwal", "2007-03-15", "Male", "manav.agarwal@demo.com", "9876543232"),
        ("Kriti Saxena", "2008-07-08", "Female", "kriti.saxena@demo.com", "9876543233"),
        ("Nikhil Bose", "2007-01-22", "Male", "nikhil.bose@demo.com", "9876543234"),
        ("Aisha Sheikh", "2008-05-30", "Female", "aisha.sheikh@demo.com", "9876543235"),
        ("Harsh Thakur", "2007-09-14", "Male", "harsh.thakur@demo.com", "9876543236"),
        ("Riya Kapoor", "2008-11-25", "Female", "riya.kapoor@demo.com", "9876543237"),
        ("Siddharth Raj", "2007-04-18", "Male", "siddharth.raj@demo.com", "9876543238"),
        ("Tanya Bhatia", "2008-12-02", "Female", "tanya.bhatia@demo.com", "9876543239"),
    ]
    for name, dob, gender, email, phone in data:
        yield _safe_create("Student", {
            "student_name": name,
            "student_email_id": email,
            "mobile_number": phone,
            "date_of_birth": dob,
            "gender": gender,
            "title": name,
        }, unique_field="student_email_id", dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CUSTOM DOCTYPES
# ═══════════════════════════════════════════════════════════════

def _create_hostels(dry_run=False):
    """Hostel (custom) — field: hostel_name, hostel__type (double underscore!)"""
    for name, htype, addr in [
        ("Boys Hostel - A", "Boys", "Main Campus, Block A"),
        ("Girls Hostel - B", "Girls", "Main Campus, Block B"),
    ]:
        yield _safe_create("Hostel", {
            "hostel_name": name,
            "hostel__type": htype,  # Note: double underscore in fieldname!
            "address": addr,
        }, unique_field="hostel_name", dry_run=dry_run)


def _create_hostel_room_types(dry_run=False):
    """Hostel Room Types (custom) — field: room_type (not hostel_room_type)"""
    for rt, cap, fee, amenities in [
        ("Single Room", 1, 8000, "Attached bathroom, Study table, Almirah"),
        ("Double Sharing", 2, 5000, "Shared bathroom, Study table, Almirah"),
        ("Triple Sharing", 3, 3500, "Common area, Shared bathroom"),
    ]:
        yield _safe_create("Hostel Room Types", {
            "room_type": rt,
            "capacity": cap,
            "monthly_fee": fee,
            "amenities": amenities,
        }, unique_field="room_type", dry_run=dry_run)


def _create_wardens(dry_run=False):
    """Warden (custom)"""
    data = [
        ("Ramesh Gupta", "WAR-001", "9876543301"),
        ("Anita Sharma", "WAR-002", "9876543302"),
    ]
    for name, w_id, phone in data:
        yield _safe_create("Warden", {
            "warden_name": name,
            "warden_id": w_id,
            "contact_number": phone,
        }, unique_field="warden_name", dry_run=dry_run)


def _create_hostel_blocks(dry_run=False):
    """Hostel Block (custom) — field: block_name, hostel (Link)"""
    hostels = frappe.db.get_all("Hostel", pluck="name") if not dry_run else ["Boys Hostel - A", "Girls Hostel - B"]
    for h in hostels:
        for bl in ["A", "B", "C"]:
            bn = f"{h} - Block {bl}"
            yield _safe_create("Hostel Block", {
                "block_name": bn,
                "hostel": h,
            }, unique_field="block_name", dry_run=dry_run)


def _create_hostel_rooms(dry_run=False):
    """Hostel Room (custom) — autoname: field:room_number"""
    hostels = frappe.db.get_all("Hostel", pluck="name") if not dry_run else ["Boys Hostel - A", "Girls Hostel - B"]
    room_types = ["1 Sharing AC", "2 Sharing-AC", "3 Sharing-AC", "4 Sharing-AC"]
    room_statuses = ["Available", "Nearly Full", "Full", "Reserved", "Maintenance"]
    for h in hostels:
        # find blocks for this hostel
        blocks = frappe.db.get_all("Hostel Block", filters={"hostel": h}, pluck="name") or ["-"]
        for floor in range(1, 4):
            for num in range(1, 6):
                rn = f"RM-{h[:3]}-{floor}{num:02d}"
                yield _safe_create("Hostel Room", {
                    "room_number": rn,
                    "hostel": h,
                    "hostel_block": random.choice(blocks),
                    "floor_number": floor,
                    "room_type": random.choice(room_types),
                    "total_beds": random.choice([1, 2, 3, 4]),
                    "occupied_beds": random.randint(0, 3),
                    "room_status": random.choice(room_statuses),
                }, unique_field="room_number", dry_run=dry_run)


def _create_mess_menu(dry_run=False):
    """Mess Menu (custom) — field: day, meal_type, menu_items"""
    for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
        for meal_type, items in [
            ("breakfast", random.choice(["Idli Sambar, Poha", "Upma, Paratha", "Dosa, Chutney", "Puri Bhaji, Tea", "Sandwich, Milk"])),
            ("luch", random.choice(["Dal Rice, Roti", "Biryani, Raita", "Chapati Curry, Salad", "Pulav, Papad", "Khichdi, Pickle"])),
            ("snacks", random.choice(["Samosa, Tea", "Biscuits, Milk", "Fruits, Juice", "Vada Pav, Coffee", "Popcorn, Lassi"])),
            ("dinner", random.choice(["Chapati Dal, Rice", "Roti Paneer, Salad", "Noodles, Soup", "Pasta, Garlic Bread", "Pulav, Raita"])),
        ]:
            yield _safe_create("Mess Menu", {
                "day": day,
                "meal_type": meal_type,
                "menu_items": items,
                "academic_year": "2026-2027",
            }, dry_run=dry_run)


def _create_transport_routes(dry_run=False):
    """Transport Route (custom) — field: route_name"""
    for name in ["North Route - A", "South Route - B", "East Route - C", "West Route - D"]:
        yield _safe_create("Transport Route", {
            "route_name": name,
            "route_status": "Active",
            "is_active": 1,
        }, unique_field="route_name", dry_run=dry_run)


def _create_transport_vehicles(dry_run=False):
    """Transport Vehicle (custom) — autoname: field:vehicle_name"""
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


def _create_book_authors(dry_run=False):
    """Book Author (custom) — naming_series, no author_name field"""
    authors = ["R.K. Narayan", "Chetan Bhagat", "Amish Tripathi", "Arundhati Roy",
               "Jhumpa Lahiri", "Vikram Seth", "Mulk Raj Anand", "Stephen Hawking",
               "R.S. Aggarwal", "A.P.J. Abdul Kalam"]
    seen = set()
    for name in authors:
        if name in seen:
            continue
        seen.add(name)
        yield _safe_create("Book Author", {
            "naming_series": "AUTH-.YYYY.-",
        }, dry_run=dry_run)


def _create_book_categories(dry_run=False):
    """Book Category (custom) — field: category_name"""
    for cat in ["Fiction", "Non-Fiction", "Science", "Mathematics", "History",
                "Literature", "Reference", "Children", "Competitive Exams"]:
        yield _safe_create("Book Category", {
            "category_name": cat,
        }, unique_field="category_name", dry_run=dry_run)


def _create_library_racks(dry_run=False):
    """Library Rack (custom) — autoname: field:rack_name"""
    for rack in ["Rack A1", "Rack A2", "Rack B1", "Rack B2", "Rack C1"]:
        yield _safe_create("Library Rack", {
            "rack_name": rack,
        }, unique_field="rack_name", dry_run=dry_run)


def _create_library_books(dry_run=False):
    """Library Book (custom) — autoincrement naming, fields: isbn, author (Link), category (Link), publisher"""
    if dry_run:
        yield "[DRY-RUN] Library books"
        return

    authors = frappe.db.get_all("Book Author", pluck="name", limit=8)
    categories = frappe.db.get_all("Book Category", pluck="name")
    racks = frappe.db.get_all("Library Rack", pluck="name")

    books = [
        ("9780140189849", "Malgudi Days", "Fiction", "Penguin", 1950),
        ("9781416562603", "The White Tiger", "Fiction", "Harper Collins", 2008),
        ("9789380658458", "The Immortals of Meluha", "Fiction", "Rupa Publications", 2010),
        ("9780006550688", "The God of Small Things", "Fiction", "Penguin", 1997),
        ("9780618101367", "Interpreter of Maladies", "Fiction", "Harper Collins", 1999),
        ("9780553380163", "A Brief History of Time", "Science", "Bantam", 1988),
        ("9788177097575", "Mathematics for Class 10", "Mathematics", "R.S. Aggarwal", 2020),
        ("9780195687859", "India's Ancient Past", "History", "Oxford Press", 2005),
        ("9788173711466", "Wings of Fire", "Non-Fiction", "Universities Press", 1999),
        ("9780143031031", "The Discovery of India", "History", "Penguin", 1946),
    ]

    author_names = [a for a in authors] if authors else []
    cat_names = [c for c in categories] if categories else []

    for isbn, title, cat, pub, year in books:
        author = random.choice(author_names) if author_names else ""
        category = cat if cat in cat_names else (cat_names[0] if cat_names else "")
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


def _create_book_copies(dry_run=False):
    """Book Copy (custom) — autoincrement"""
    if dry_run:
        yield "[DRY-RUN] Book copies"
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


def _create_library_members(dry_run=False):
    """Library Member (custom) — field: member_id"""
    if dry_run:
        for i in range(5):
            yield f"[DRY-RUN] Library member LIB-MEM-{i+1}"
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


def _create_fee_categories(dry_run=False):
    """Fee Category (standard)"""
    for fc in ["Tuition Fee", "Development Fee", "Computer Lab Fee",
               "Library Fee", "Sports Fee", "Transport Fee", "Exam Fee"]:
        yield _safe_create("Fee Category", {
            "fee_category": fc,
        }, unique_field="fee_category", dry_run=dry_run)


def _create_fee_structures(dry_run=False):
    """Fee Structure (standard) — with child table components"""
    if dry_run:
        yield "[DRY-RUN] Fee structures"
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


def _create_exam_terms(dry_run=False):
    """Exam Term (custom) — field: term_name"""
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


def _create_exam_halls(dry_run=False):
    """Exam Hall (custom)"""
    for hall_name, cap in [
        ("Main Hall", 120),
        ("Examination Hall A", 60),
        ("Examination Hall B", 60),
    ]:
        yield _safe_create("Exam Hall", {
            "hall_name": hall_name,
            "capacity": cap,
        }, unique_field="hall_name", dry_run=dry_run)


def _create_event_types(dry_run=False):
    """Event Type (custom)"""
    for name in ["Assembly", "Sports Day", "Cultural Event", "PTA Meeting",
                 "Science Fair", "Field Trip", "Workshop"]:
        yield _safe_create("Event Type", {
            "event_type_name": name,
        }, unique_field="event_type_name", dry_run=dry_run)


def _create_ai_settings(dry_run=False):
    """AI Settings (custom, Single) — not really insertable as singular"""
    if not dry_run and not frappe.db.exists("AI Settings", ""):
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
            yield None
    else:
        yield None


def _create_gamification_settings(dry_run=False):
    """Gamification Settings (custom, Single)"""
    if not dry_run and not frappe.db.exists("Gamification Settings", ""):
        try:
            doc = frappe.get_single("Gamification Settings")
            doc.update({
                "setting_name": "Gamification Settings",
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


def _create_badge_definitions(dry_run=False):
    """Badge Definition (custom) — has required criteria_type"""
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
            "badge_color": random.choice(["#FFD700", "#C0C0C0", "#CD7F32", "#4CAF50", "#2196F3"]),
            "is_active": 1,
        }, unique_field="badge_name", dry_run=dry_run)


def _create_student_points_ledger(dry_run=False):
    """Student Points Ledger (custom)"""
    if dry_run:
        yield "[DRY-RUN] Points ledger"
        return
    students = frappe.db.get_all("Student", pluck="name", limit=5)
    for stu in students:
        yield _safe_create("Student Points Ledger", {
            "student": stu,
            "points": random.randint(50, 500),
            "reason": "Demo data initialization",
            "date": date(2026, 4, 1),
        }, dry_run=dry_run)


def _create_compliance_certifications(dry_run=False):
    """Compliance Certification (custom, submittable)"""
    for name, stype, body, status in [
        ("ISO 27001:2022", "ISO 27001", "TUV Rheinland", "Active"),
        ("GDPR Readiness", "GDPR", "Data Protection Office", "Active"),
        ("FERPA Compliance", "FERPA", "Education Department", "Active"),
    ]:
        yield _safe_create("Compliance Certification", {
            "certification_name": name,
            "standard_type": stype,
            "certifying_body": body,
            "issue_date": date(2025, 1, 1),
            "expiry_date": date(2028, 1, 1),
            "status": status,
            "is_compliant": 1,
        }, unique_field="certification_name", submit=True, dry_run=dry_run)


def _create_board_meetings(dry_run=False):
    """Board Meeting (custom, submittable) — naming_series based"""
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


def _create_committee_definitions(dry_run=False):
    """Committee Definition (custom) — field: committee_name"""
    for name, ctype in [
        ("Academic Committee", "Academic Council"),
        ("Finance Committee", "Finance Committee"),
        ("Disciplinary Committee", "Disciplinary Committee"),
        ("Sports Committee", "Sports Committee"),
    ]:
        yield _safe_create("Committee Definition", {
            "committee_name": name,
            "committee_type": ctype,
            "purpose": f"Oversee {name.lower()} matters and provide strategic guidance.",
        }, unique_field="committee_name", dry_run=dry_run)


def _create_asset_register(dry_run=False):
    """Asset Register (custom, submittable) — field: asset_code"""
    for name, code, cat, cost in [
        ("Smart Board - Class A1", "AST-001", "Electronics", 50000),
        ("Computer Lab Desktops (Set)", "AST-002", "IT Equipment", 250000),
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


def _create_asset_maintenance(dry_run=False):
    """Asset Maintenance (custom, submittable) — field: maintenance_id"""
    if dry_run:
        yield "[DRY-RUN] Asset maintenance"
        return
    assets = frappe.db.get_all("Asset Register", pluck="name", limit=3)
    for i, asset in enumerate(assets):
        mid = f"MAINT-{i+1:04d}"
        yield _safe_create("Asset Maintenance", {
            "maintenance_id": mid,
            "asset_code": asset,
            "maintenance_type": "Preventive",
            "issue_description": "Regular maintenance check",
            "maintenance_date": date(2026, random.randint(1, 6), random.randint(1, 28)),
            "status": "Completed",
        }, unique_field="maintenance_id", submit=True, dry_run=dry_run)


def _create_biometric_devices(dry_run=False):
    """Biometric Device (custom) — field: device_name"""
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


def _create_alumni_records(dry_run=False):
    """Alumni Record (custom) — field: alumni_id"""
    data = [
        ("Rahul Verma", 2020, "Software Engineer", "Tech Corp"),
        ("Priya Patel", 2019, "Doctor", "City Hospital"),
        ("Amit Kumar", 2021, "Business Analyst", "Finance Ltd"),
        ("Sneha Reddy", 2020, "Teacher", "Public School"),
    ]
    for i, (name, year, occ, org) in enumerate(data):
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


def _create_question_bank(dry_run=False):
    """Question Bank (custom) — field: question_title; has required question_text"""
    if dry_run:
        yield "[DRY-RUN] Questions"
        return

    # Find courses to link
    courses = frappe.db.get_all("Course", pluck="name", limit=10)

    questions = [
        ("What is the capital of France?", "Multiple Choice",
         "Paris is the capital of France.", 2, ["London", "Paris", "Berlin", "Madrid"], 2),
        ("What is 5 + 7?", "Short Answer", "Basic addition", 1, None, 0),
        ("The Earth revolves around the Sun.", "True/False", "True", 1, None, 0),
        ("Explain photosynthesis", "Long Answer",
         "Plants convert light energy into chemical energy", 5, None, 0),
        ("Which planet is known as Red Planet?", "Single Choice",
         "Mars is the Red Planet", 2, ["Venus", "Mars", "Jupiter", "Saturn"], 2),
        ("Water boils at 100°C", "True/False", "True at sea level", 1, None, 0),
    ]

    for q_title, q_type, answer, marks, options, ans_idx in questions:
        course = random.choice(courses) if courses else ""
        yield _safe_create("Question Bank", {
            "question_title": q_title,
            "question_type": q_type,
            "question_text": f"<p>{q_title}</p>",
            "subject": course,
            "marks": marks,
            "difficulty_level": random.choice(["Easy", "Medium", "Hard"]),
            "correct_answer": answer,
        }, unique_field="question_title", dry_run=dry_run)


def _create_course_modules(dry_run=False):
    """Course Module (custom) — field: module_title; requires course field"""
    if dry_run:
        yield "[DRY-RUN] Course modules"
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


def _create_assignments(dry_run=False):
    """Assignment (custom, submittable) — field: assignment_title"""
    if dry_run:
        yield "[DRY-RUN] Assignments"
        return

    courses = frappe.db.get_all("Course", pluck="name", limit=4)
    instructors = frappe.db.get_all("Instructor", pluck="name", limit=3)

    for i, title in enumerate([
        "Mathematics Homework - Week 1",
        "Science Lab Report",
        "English Essay Assignment",
        "History Project",
    ]):
        course = courses[i % len(courses)] if courses else ""
        instr = instructors[i % len(instructors)] if instructors else ""
        yield _safe_create("Assignment", {
            "assignment_title": title,
            "course": course,
            "instructor": instr,
            "description": f"Complete the {title} as per instructions.",
            "due_date": date(2026, 5, 15 + i * 7),
            "max_score": 100,
            "allow_late_submission": 1,
        }, unique_field="assignment_title", submit=True, dry_run=dry_run)


def _create_school_events(dry_run=False):
    """School Event (custom) — hash naming"""
    events = [
        ("Annual Day Celebration", "Assembly", date(2026, 12, 15), date(2026, 12, 15),
         "Main Auditorium", "Upcoming"),
        ("Sports Day", "Sports Day", date(2026, 11, 20), date(2026, 11, 22),
         "School Ground", "Upcoming"),
        ("Science Fair", "Science Fair", date(2026, 10, 5), date(2026, 10, 5),
         "Science Lab Block", "Upcoming"),
    ]
    for title, etype, start_dt, end_dt, venue, status in events:
        yield _safe_create("School Event", {
            "title": title,
            "event_type": etype,
            "start_date": start_dt,
            "end_date": end_dt,
            "venue": venue,
            "status": status,
            "audience": "Everybody",
            "academic_year": "2026-2027",
        }, dry_run=dry_run)


def _create_student_fee_installments(dry_run=False):
    """Student Fee Installment (custom) — hash naming"""
    if dry_run:
        yield "[DRY-RUN] Fee installments"
        return

    students = frappe.db.get_all("Student", pluck="name", limit=5)
    for stu in students:
        categories_map = {
            "Tuition Fee": 2500,
            "Development Fee": 1000,
            "Library Fee": 300,
            "Sports Fee": 200,
        }
        for cat, amt in categories_map.items():
            yield _safe_create("Student Fee Installment", {
                "fee_category": cat,
                "due_date": random.choice([date(2026, 5, 15), date(2026, 8, 15), date(2026, 11, 15)]),
                "amount": amt,
                "status": "Pending",
                "outstanding_amount": amt,
            }, dry_run=dry_run)


def _create_visitor_logs(dry_run=False):
    """Visitor Log (custom) — auto naming"""
    visitors = [
        ("Rahul's Father", "9876543401", "Principal", "Parent Meeting", "Checked In"),
        ("Book Supplier", "9876543402", "Admin Office", "Book Delivery", "Checked In"),
        ("Sports Coach", "9876543403", "Sports Department", "Coaching Session", "Checked Out"),
    ]
    for name, phone, visit_to, purpose, status in visitors:
        yield _safe_create("Visitor Log", {
            "visitor_name": name,
            "contact_number": phone,
            "visiting_to": visit_to,
            "purpose": purpose,
            "in_time": datetime(2026, 4, random.randint(1, 30), random.randint(8, 16), 0),
            "status": status,
        }, dry_run=dry_run)


def _create_call_logs(dry_run=False):
    """Call Log (custom) — auto naming"""
    calls = [
        ("Parent - Arjun Mehta", "9876543220", "Incoming", "Fee Inquiry"),
        ("Vendor - Stationery", "9876543405", "Incoming", "Supply Order"),
        ("Transport Dept", "9876543406", "Outgoing", "Bus Route Confirmation"),
    ]
    for caller, phone, ctype, purpose in calls:
        yield _safe_create("Call Log", {
            "caller_name": caller,
            "contact_number": phone,
            "call_type": ctype,
            "purpose": purpose,
            "call_date": date(2026, 4, random.randint(1, 15)),
        }, dry_run=dry_run)


def _create_postal_records(dry_run=False):
    """Postal Record (custom) — auto naming"""
    records = [
        ("Incoming", "Education Board", "Exam Results Notification"),
        ("Outgoing", "Parent Association", "PTM Invitation"),
        ("Confidential", "Management", "Board Meeting Minutes"),
    ]
    for ptype, sender, subject in records:
        yield _safe_create("Postal Record", {
            "postal_type": ptype,
            "sender_recipient": sender,
            "subject": subject,
            "date": date(2026, 4, random.randint(1, 15)),
        }, dry_run=dry_run)


def _create_admission_enquiries(dry_run=False):
    """Admission Enquiry (custom) — field: enquiry_id"""
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


def _create_student_certificates(dry_run=False):
    """Student Certificate (custom) — naming_series: SCRT"""
    if dry_run:
        yield "[DRY-RUN] Student certificates"
        return

    students = frappe.db.get_all("Student", pluck="name", limit=5)
    # Ensure certificate template exists
    if not frappe.db.exists("Certificate Template", "Bonafide Certificate"):
        frappe.get_doc({
            "doctype": "Certificate Template",
            "template_name": "Bonafide Certificate",
            "template_type": "Bonafide",
        }).insert(ignore_permissions=True)

    for stu in students:
        yield _safe_create("Student Certificate", {
            "naming_series": "SCRT-.YYYY.-",
            "student": stu,
            "template": "Bonafide Certificate",
        }, dry_run=dry_run)


def _create_grievances(dry_run=False):
    """Grievance Box (custom)"""
    grievances = [
        ("Room A/C not working", "Maintenance", "High"),
        ("Mess food quality", "Mess", "Medium"),
        ("Broken window in Room 102", "Maintenance", "Low"),
    ]
    for desc, cat, priority in grievances:
        yield _safe_create("Grievance Box", {
            "description": desc,
            "complaint_type": "Maintenance" if cat == "Maintenance" else "Food",
            "category": cat,
            "priority": priority,
            "complaint_date": date(2026, 4, random.randint(1, 10)),
            "status": "Open",
        }, dry_run=dry_run)


def _create_student_transport_assignments(dry_run=False):
    """Student Transport Assignment (custom, submittable)"""
    if dry_run:
        yield "[DRY-RUN] Transport assignments"
        return

    students = frappe.db.get_all("Student", pluck="name", limit=3)
    routes = frappe.db.get_all("Transport Route", pluck="name", limit=2)
    for stu in students:
        route = random.choice(routes) if routes else ""
        yield _safe_create("Student Transport Assignment", {
            "student": stu,
            "student_name": stu,
            "transport_route": route,
            "transport_mode": "School Bus",
            "is_active": 1,
            "assigned_date": date(2026, 4, 1),
        }, submit=True, dry_run=dry_run)


def _create_response_templates(dry_run=False):
    """Response Template (custom)"""
    for name, ctype, msg in [
        ("Fee Reminder", "Fee", "Dear Parent, kindly pay the pending fee by the due date."),
        ("Attendance Alert", "Attendance",
         "Your ward was absent on {date}. Kindly send a leave note."),
        ("Event Notification", "Event",
         "Dear Parent, {event_name} is scheduled on {date}. Your participation is requested."),
    ]:
        yield _safe_create("Response Template", {
            "template_name": name,
            "type": ctype,
            "message": msg,
        }, unique_field="template_name", dry_run=dry_run)


def _create_vehicle_gps_logs(dry_run=False):
    """Vehicle GPS Tracking Log (custom)"""
    if dry_run:
        yield "[DRY-RUN] GPS logs"
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
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def generate(dry_run=False, verbose=True):
    """Generate all demo data."""
    print("=" * 60)
    print("SCHOOL MANAGEMENT SOFTWARE - DEMO DATA GENERATOR")
    if dry_run:
        print("  *** DRY RUN MODE - No data will be inserted ***")
    print("=" * 60)

    sections = [
        # Standard Masters (ERPNext / Education)
        lambda: _create_academic_years(dry_run),
        lambda: _create_academic_terms(dry_run),
        lambda: _create_programs(dry_run),
        lambda: _create_courses(dry_run),
        lambda: _create_student_groups(dry_run),
        lambda: _create_instructors(dry_run),
        lambda: _create_rooms(dry_run),
        lambda: _create_grading_scale(dry_run),
        lambda: _create_fee_categories(dry_run),

        # Guardians
        lambda: _create_guardians(dry_run),

        # Students
        lambda: _create_students(dry_run),

        # Fee
        lambda: _create_fee_structures(dry_run),

        # Custom: Hostel
        lambda: _create_hostels(dry_run),
        lambda: _create_hostel_room_types(dry_run),
        lambda: _create_wardens(dry_run),
        lambda: _create_hostel_blocks(dry_run),
        lambda: _create_hostel_rooms(dry_run),
        lambda: _create_mess_menu(dry_run),

        # Custom: Transport
        lambda: _create_transport_routes(dry_run),
        lambda: _create_transport_vehicles(dry_run),

        # Custom: Library
        lambda: _create_book_authors(dry_run),
        lambda: _create_book_categories(dry_run),
        lambda: _create_library_racks(dry_run),
        lambda: _create_library_books(dry_run),
        lambda: _create_book_copies(dry_run),
        lambda: _create_library_members(dry_run),

        # Custom: Exam
        lambda: _create_exam_terms(dry_run),
        lambda: _create_exam_halls(dry_run),

        # Custom: Events
        lambda: _create_event_types(dry_run),
        lambda: _create_school_events(dry_run),

        # Custom: AI & Gamification
        lambda: _create_ai_settings(dry_run),
        lambda: _create_gamification_settings(dry_run),
        lambda: _create_badge_definitions(dry_run),
        lambda: _create_student_points_ledger(dry_run),

        # Custom: Governance
        lambda: _create_committee_definitions(dry_run),
        lambda: _create_board_meetings(dry_run),
        lambda: _create_compliance_certifications(dry_run),

        # Custom: Assets
        lambda: _create_asset_register(dry_run),
        lambda: _create_asset_maintenance(dry_run),

        # Custom: Biometric
        lambda: _create_biometric_devices(dry_run),

        # Custom: Alumni
        lambda: _create_alumni_records(dry_run),

        # Custom: LMS
        lambda: _create_question_bank(dry_run),
        lambda: _create_course_modules(dry_run),
        lambda: _create_assignments(dry_run),

        # Custom: Front Office
        lambda: _create_visitor_logs(dry_run),
        lambda: _create_call_logs(dry_run),
        lambda: _create_postal_records(dry_run),
        lambda: _create_admission_enquiries(dry_run),
        lambda: _create_response_templates(dry_run),
        lambda: _create_grievances(dry_run),

        # Custom: Certificates
        lambda: _create_student_certificates(dry_run),

        # Custom: Transport Operations
        lambda: _create_student_transport_assignments(dry_run),
        lambda: _create_vehicle_gps_logs(dry_run),

        # Custom: Fees
        lambda: _create_student_fee_installments(dry_run),
    ]

    results = []
    for sec_fn in sections:
        name = sec_fn.__name__.replace("_create_", "").replace("_", " ").title()
        result = _exec(name, sec_fn, verbose)
        results.append(result)
        frappe.db.commit()
        if verbose:
            print(f"  {name:50s} ✅ {result['created']} created, "
                  f"{result['skipped']} skipped"
                  + (f", ⚠️ {len(result['errors'])} errors" if result['errors'] else ""))

    _report(results, verbose)

    if not dry_run:
        print("\n💡 Demo data created successfully!")
        print("   Run 'bench clear-cache' if some records don't appear immediately.")
    else:
        print("\n💡 Dry-run complete. No data was inserted.")

    return results


if __name__ == "__main__":
    generate()
