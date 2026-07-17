import frappe
import os
from frappe.modules.import_file import import_file_by_path


def after_migrate_setup():
    """Run after bench migrate to create missing modules and sync new doctypes."""
    app_name = "school_management_software"
    created_modules = []

    # 1. Create Module Def records for new modules
    modules = {
        "School Compliance": "Compliance & Certification Management",
        "School Governance": "Board & Committee Governance Tools",
        "School Assets": "Asset Lifecycle Management",
        "School Transport": "Transport & GPS Tracking",
        "Student Fees": "Student Fee Management",
    }

    for module_name, module_desc in modules.items():
        if not frappe.db.exists("Module Def", module_name):
            module_doc = frappe.get_doc(
                {
                    "doctype": "Module Def",
                    "module_name": module_name,
                    "app_name": app_name,
                    "custom": 0,
                }
            )
            module_doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
            created_modules.append(module_name)
            print(f"Created Module Def: {module_name}")

    # 2. Force-sync all new doctypes from JSON files
    new_doctypes = [
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

    app_path = frappe.get_app_path(app_name)

    for doctype_name in new_doctypes:
        doctype_folder = frappe.scrub(doctype_name)
        json_path = os.path.join(
            app_path, "doctype", doctype_folder, f"{doctype_folder}.json"
        )

        if not os.path.exists(json_path):
            print(f"JSON not found: {json_path}")
            continue

        try:
            import_file_by_path(json_path, force=True)
            status = "Re-synced" if frappe.db.exists("DocType", doctype_name) else "Created"
            print(f"{status}: {doctype_name}")
        except Exception as e:
            frappe.log_error(
                message=f"Error syncing {doctype_name}: {e}",
                title="School Management - after_migrate",
            )
            print(f"Error syncing {doctype_name}: {e}")

    frappe.db.commit()

    # 3. Sync workspace JSONs for new modules
    new_workspaces = [
        "School Governance",
        "School Compliance",
        "School Assets",
        "School Transport",
    ]

    for workspace_name in new_workspaces:
        workspace_folder = frappe.scrub(workspace_name)
        json_path = os.path.join(
            app_path, "workspace", workspace_folder, f"{workspace_folder}.json"
        )

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
            print(f"Error syncing workspace {workspace_name}: {e}")

    frappe.db.commit()

    # 4. Also sync the student_fees workspace (updated module)
    student_fees_path = os.path.join(
        app_path, "workspace", "student_fees", "student_fees.json"
    )
    if os.path.exists(student_fees_path):
        try:
            import_file_by_path(student_fees_path, force=True)
            print("Synced workspace: Student Fees")
        except Exception as e:
            frappe.log_error(
                message=f"Error syncing Student Fees workspace: {e}",
                title="School Management - after_migrate",
            )

    frappe.db.commit()

    # 5. Add Table custom field linking Student to Student Fee Installment
    if frappe.db.exists("DocType", "Student Fee Installment"):
        if not frappe.db.exists(
            "Custom Field", {"dt": "Student", "fieldname": "fee_installments"}
        ):
            try:
                cf = frappe.get_doc({
                    "doctype": "Custom Field",
                    "dt": "Student",
                    "fieldname": "fee_installments",
                    "label": "Fee Installments",
                    "fieldtype": "Table",
                    "options": "Student Fee Installment",
                    "insert_after": "fee_staus",
                    "module": "Student Fees",
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

    if created_modules:
        print(f"Created {len(created_modules)} new modules: {', '.join(created_modules)}")
    else:
        print("All modules already exist.")
