# School Management - Frappe App
# Auto-generated from Excel customization exports for ERPNext v15 Education module

app_name = "school_management_software"
app_title = "School Management"
app_publisher = "School Management"
app_description = "School Management Software - Custom ERPNext Education Module with Admissions, Hostel, Library, Transport, Events, Exams, and more"
app_email = "admin@schoolmanagement.com"
app_license = "MIT"

# Fixtures for customizations that are not auto-discovered during bench migrate.
# DocTypes, Reports, Print Formats, and Workspaces are auto-discovered from their
# respective folders (doctype/, report/, print_format/, workspace/).
# Server Scripts and Client Scripts MUST be listed here to be installed.
fixtures = [
    # Server Scripts — files live in server_script/name/name.json
    {"dt": "Server Script", "path": "server_script"},

    # Client Scripts — files live in client_script/name/name.json
    {"dt": "Client Script", "path": "client_script"},
]

after_migrate = []
