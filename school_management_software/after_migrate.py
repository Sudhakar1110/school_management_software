import frappe
import os
from frappe.modules.import_file import import_file_by_path


def after_migrate_setup():
    """Run after bench migrate to sync all custom doctypes from JSON files."""
    app_name = "school_management_software"
    app_path = frappe.get_app_path(app_name)

    # All custom doctypes from git repo that may not be synced to site yet
    all_custom_doctypes = [
        # Front Office & Admissions
        "Admission Enquiry",
        "Call Log",
        "Postal Record",
        "Visitor Log",
        "Response Template",

        # AI & Gamification
        "AI Settings",
        "Badge Definition",
        "Gamification Settings",
        "Student Points Ledger",

        # Academic - Assignments & Assessment
        "Assignment",
        "Assignment Rubric",
        "Assignment Submission",
        "Assessment Group",

        # Course Modules (LMS)
        "Course Module",
        "Course Module Content",
        "Course Module Prerequisite",

        # Assessment - Question Bank
        "Question Bank",
        "Question Bank Option",

        # Biometric
        "Biometric Attendance Log",
        "Biometric Device",

        # Alumni
        "Alumni Record",

        # Gap Analysis Features (may already exist, sync to be safe)
        "Compliance Certification",
        "Compliance Policy Link",
        "Board Meeting",
        "Board Meeting Agenda",
        "Meeting Attendee",
        "Committee Definition",
        "Asset Register",
        "Asset Maintenance",
        "Vehicle GPS Tracking Log",
        "Student Fee Installment",
    ]

    for doctype_name in all_custom_doctypes:
        doctype_folder = frappe.scrub(doctype_name)
        json_path = os.path.join(app_path, "doctype", doctype_folder, f"{doctype_folder}.json")

        if not os.path.exists(json_path):
            print(f"JSON not found: {json_path}")
            continue

        try:
            already_exists = frappe.db.exists("DocType", doctype_name)
            import_file_by_path(json_path, force=True)
            status = "Re-synced" if already_exists else "CREATED"
            print(f"{status}: {doctype_name}")
        except Exception as e:
            frappe.log_error(
                message=f"Error syncing {doctype_name}: {e}",
                title="School Management - after_migrate",
            )
            print(f"ERROR: {doctype_name} - {e}")

    frappe.db.commit()

    # Sync all workspace JSONs so module pages appear in sidebar
    # Note: Manual folder mapping needed because frappe.scrub() keeps & in names
    workspace_folders = {
        "Home": "home",
        "School Management Software": "school_management_software",
        "Admissions": "admissions",
        "Attendance & Assessments": "attendance_assessments",
        "Exam": "exam",
        "Hostel-Management": "hostel_management",
        "Library": "library",
        "Masters": "masters",
        "Overview": "overview",
        "School Events": "school_events",
        "Student Fees": "student_fees",
        "Student & Scheduling": "student_scheduling",
        "Transport": "transport",
        "School Governance": "school_governance",
        "School Compliance": "school_compliance",
        "School Assets": "school_assets",
        "School Transport": "school_transport",
    }

    for workspace_name, workspace_folder in workspace_folders.items():
        json_path = os.path.join(app_path, "workspace", workspace_folder, f"{workspace_folder}.json")

        if not os.path.exists(json_path):
            print(f"Workspace JSON not found: {json_path}")
            continue

        try:
            import_file_by_path(json_path, force=True)
            print(f"Synced workspace: {workspace_name}")
        except Exception as e:
            frappe.log_error(
                message=f"Error syncing workspace {workspace_name}: {e}",
                title="School Management - after_migrate",
            )
            print(f"ERROR: workspace {workspace_name} - {e}")

    frappe.db.commit()

    # Ensure the Module Def has the correct app_name for sidebar visibility
    if frappe.db.exists("Module Def", "School Management Software"):
        current_app = frappe.db.get_value("Module Def", "School Management Software", "app_name")
        if current_app != app_name:
            frappe.db.set_value("Module Def", "School Management Software", "app_name", app_name)
            print(f"Fixed Module Def app_name: {current_app} -> {app_name}")

    frappe.db.commit()

    # Add Table custom field linking Student to Student Fee Installment
    if frappe.db.exists("DocType", "Student Fee Installment"):
        if not frappe.db.exists("Custom Field", {"dt": "Student", "fieldname": "fee_installments"}):
            try:
                cf = frappe.get_doc({
                    "doctype": "Custom Field",
                    "dt": "Student",
                    "fieldname": "fee_installments",
                    "label": "Fee Installments",
                    "fieldtype": "Table",
                    "options": "Student Fee Installment",
                    "insert_after": "fee_staus",
                    "module": "School Management Software",
                })
                cf.insert(ignore_permissions=True)
                print("Added Fee Installments table field to Student")
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(
                    message=f"Error creating Fee Installments table field: {e}",
                    title="School Management - after_migrate",
                )
                print(f"Error creating Fee Installments table field: {e}")
        else:
            print("Fee Installments table field already exists on Student")
