import frappe
import os
from frappe.modules.import_file import import_file_by_path


def after_migrate_setup():
    """Run after bench migrate to sync new doctypes and create helper fields."""
    app_name = "school_management_software"
    app_path = frappe.get_app_path(app_name)

    # 1. Force-sync all new gap analysis doctypes from JSON files
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

    for doctype_name in new_doctypes:
        doctype_folder = frappe.scrub(doctype_name)
        json_path = os.path.join(app_path, "doctype", doctype_folder, f"{doctype_folder}.json")

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

    # 2. Add Table custom field linking Student to Student Fee Installment
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
