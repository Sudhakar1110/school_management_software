# School Management - Frappe App
# Auto-generated from Excel customization exports for ERPNext v15 Education module

app_name = "school_management_software"
app_title = "School Management"
app_publisher = "School Management"
app_description = "School Management Software - Custom ERPNext Education Module with Admissions, Hostel, Library, Transport, Events, Exams, and more"
app_email = "admin@schoolmanagement.com"
app_license = "MIT"

required_apps = ["erpnext", "education"]


# Fixtures for customizations that are not auto-discovered during bench migrate.
# DocTypes, Reports, Print Formats, and Workspaces are auto-discovered from their
# respective folders (doctype/, report/, print_format/, workspace/).
# Server Scripts and Client Scripts MUST be listed here to be installed.
fixtures = [
    # Custom Fields and Property Setters
    "Custom Field",
    "Property Setter",

    # Client Scripts — files live in client_script/name/name.json
    {"dt": "Client Script", "path": "client_script"},
]

after_migrate = ["school_management_software.after_migrate.after_migrate_setup"]

doc_events = {
    "Program Enrollment": {
        "before_save": "school_management_software.school_management_software.events.before_save_submitted_document_approved",
        "on_submit": "school_management_software.school_management_software.events.on_submit_auto_create_sales_invoice_on_submit",
        "before_submit": "school_management_software.school_management_software.events.before_submit_sync_data_when_enrollment_is_submitted"
    },
    "Hostel Room": {
        "before_save": "school_management_software.school_management_software.events.before_save_submitted_document_auto_calculate_everything",
        "validate": "school_management_software.school_management_software.events.validate_to_keep_room_display_updated_automatically"
    },
    "Student": {
        "on_update": "school_management_software.school_management_software.events.on_update_auto_create_alumni_record_on_student_exit",
        "on_submit": "school_management_software.school_management_software.events.on_submit_fee_auto_calculation"
    },
    "Hostel Application": {
        "on_update": "school_management_software.school_management_software.events.on_update_auto_create_hostel_admission_on_approve",
        "before_insert": "school_management_software.school_management_software.events.before_insert_block_duplicate_applications"
    },
    "Hostel Leaves": {
        "before_insert": "school_management_software.school_management_software.events.before_insert_auto_generate_gate_pass_number_on_approval"
    },
    "Student Applicant": {
        "validate": "school_management_software.school_management_software.events.validate_auto_populate_document_rows_on_new_form"
    },
    "Book Issue": {
        "on_submit": "school_management_software.school_management_software.events.on_submit_book_issue___mark_copy_as_issued",
        "before_save": "school_management_software.school_management_software.events.before_save_submitted_document_book_issue___validate___set_due_date"
    },
    "Book Return": {
        "on_submit": "school_management_software.school_management_software.events.on_submit_book_return___release_book_copy",
        "after_insert": "school_management_software.school_management_software.events.after_insert_create_fine_on_book_return"
    },
    "Grievance Box": {
        "after_save": "school_management_software.school_management_software.events.after_save_submitted_document_complaint_assigned_and_to_notify_maintenance"
    },
    "Hostel Check-Out": {
        "on_submit": "school_management_software.school_management_software.events.on_submit_frees_the_room_if_the_student_check_out"
    },
    "Hostel Admission": {
        "after_save": "school_management_software.school_management_software.events.after_save_submitted_document_handle_the_actual_check_in_transition",
        "on_submit": "school_management_software.school_management_software.events.on_submit_to_update_room_occupancy"
    },
    "Library Fine": {
        "validate": "school_management_software.school_management_software.events.validate_library_fine___process_payment"
    },
    "School Event": {
        "after_save": "school_management_software.school_management_software.events.after_save_submitted_document_notification_script"
    },
    "Student Transport Assignment": {
        "validate": "school_management_software.school_management_software.events.validate_prevent_duplicate_active_assignments"
    },
    "Student Certificate": {
        "before_insert": "school_management_software.school_management_software.events.before_insert_prevent_duplicate_certificates"
    },
    "Student Event": {
        "on_submit": "school_management_software.school_management_software.events.on_submit_student_event_celebration"
    },
    "Hall Allocation": {
        "validate": "school_management_software.school_management_software.events.validate_validate_hall_capacity"
    }
}
