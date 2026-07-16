# School Management - Frappe App
# Auto-generated from Excel customization exports for ERPNext v15 Education module

app_name = "school_management_software"
app_title = "School Management"
app_publisher = "School Management"
app_description = "School Management Software - Custom ERPNext Education Module with Admissions, Hostel, Library, Transport, Events, Exams, and more"
app_email = "admin@schoolmanagement.com"
app_license = "MIT"

# Fixtures for customizations - these auto-install on app migration
fixtures = [
    # All Custom DocTypes (new DocTypes created for this app)
    {"dt": "DocType", "filters": [["name", "in", [
        "Admit Card Template",
        "Applicant Fee",
        "Assessment Group",
        "Book Author",
        "Book Category",
        "Book Copy",
        "Book Issue",
        "Book return",
        "Certificate Template",
        "Course Schedule Slot",
        "Create Admission",
        "Custom Course Schedule",
        "Custom Program Enrollment",
        "Custom Student",
        "Custom Student Fee Installment",
        "Custom Student Guardian",
        "Custom Student Sibling",
        "Custom Timetable Detail",
        "Employee Certificate",
        "Employee ID Card",
        "Event Attachment",
        "Event Gallery",
        "Event Participant",
        "Event Type",
        "Exam Attendance",
        "Exam Hall",
        "Exam Schedule",
        "Exam Term",
        "Fine Doctypes",
        "Gate Pass",
        "Grievance Box",
        "Guardian Profile",
        "Guardian Profile Interest",
        "Guardian Profile Student",
        "Hall Allocation",
        "Hall Allocation Student",
        "Hall Ticket",
        "Hall Ticket Subject",
        "Hostel",
        "Hostel Admission",
        "Hostel Application",
        "Hostel Asset Issue",
        "Hostel Asset Issue Item",
        "Hostel Attendance",
        "Hostel Bed",
        "Hostel Block",
        "Hostel Card",
        "Hostel Check-Out",
        "Hostel Fee",
        "Hostel leaves",
        "Hostel Medical Incident",
        "Hostel Room",
        "Hostel Room Types",
        "Hostel Visitor Log",
        "ID Card Template",
        "Kit Item Detail",
        "Library Book",
        "Library fine",
        "Library Member",
        "Library Rack",
        "Library Settings",
        "Meeting Child Table",
        "Meeting Schedule",
        "Mess Attendance",
        "Mess Menu",
        "Program Student Entry",
        "Report Card",
        "Report Card Subject",
        "Report Card Trait",
        "Room Inspection",
        "Room Transfer",
        "School Event",
        "Student Admit Card",
        "Student Certificate",
        "student documents",
        "Student Event",
        "Student ID Card",
        "Student ID Card Batch",
        "Student ID Card Batch Item",
        "Student Kit Issue",
        "Student Progress Card",
        "Student Progress Card Detail",
        "Student Rank",
        "Student Transport Assignment",
        "Teacher Weekly Schedule",
        "Trait Entry",
        "Trait Entry Detail",
        "Trait Master",
        "Transport Fee",
        "Transport Route",
        "Transport Stop",
        "Transport Vehicle",
        "Warden"
    ]]]},

    # Custom Server Scripts (by name prefix to avoid picking up existing ERPNext scripts)
    {"dt": "Server Script", "filters": [
        ["script_type", "=", "DocType Event"],
        ["module", "=", "Education"]
    ]},

    # Custom Client Scripts
    {"dt": "Client Script", "filters": [
        ["module", "=", "Education"]
    ]},

    # Custom Workspaces
    {"dt": "Workspace", "filters": [["name", "in", [
        "Admissions",
        "Attendance & Assessments",
        "Exam",
        "Home",
        "Hostel Management",
        "Library",
        "Masters",
        "Overview",
        "School Events",
        "Student Fees",
        "Student & Scheduling",
        "Transport"
    ]]]}
]

# No after_migrate needed - all customizations are handled via fixtures
# DocTypes, Custom Fields, Server Scripts, Client Scripts are all fixture-based
after_migrate = []
