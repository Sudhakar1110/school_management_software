import frappe
from frappe.utils import nowdate, getdate
from frappe import _

def execute_script(doc, method=None, script=None):
    # Wrapper to execute arbitrary code (fallback)
    loc = {'doc': doc, 'frappe': frappe, 'method': method}
    exec(script, globals(), loc)

def before_save_submitted_document_approved(doc, method=None):
    # From Server Script: approved
    # Use Create Admission if it exists, otherwise fall back to Student Admission
    if frappe.db.exists("DocType", "Create Admission"):
        admission_status = frappe.db.get_value("Create Admission", doc.student_admission, "application_status")
    else:
        admission_status = frappe.db.get_value("Student Applicant", doc.student_admission, "application_status") if doc.student_admission else None
    
    if admission_status and admission_status != "Approved":
        frappe.throw("Cannot create/save enrollment. The linked admission application status is '{0}', it must be 'Approved'.".format(admission_status))

def before_save_submitted_document_auto_calculate_everything(doc, method=None):
    # From Server Script: auto-calculate everything
    if doc.is_new():
        doc.occupied_beds = 0
        doc.available_beds = doc.total_beds or 0
        doc.room_status = "Available" if (doc.total_beds or 0) > 0 else "Maintenance"
    else:
        old_doc = doc.get_doc_before_save()
        if old_doc and old_doc.total_beds != doc.total_beds:
            occupied = frappe.db.count("Hostel Admission", {
                "hostel_room": doc.name,
                "admission_status": "Checked In"
            })
            if (doc.total_beds or 0) < occupied:
                frappe.throw(
                    f"Cannot reduce Total Beds to {doc.total_beds}. "
                    f"{occupied} students are currently Checked In to this room."
                )
            doc.occupied_beds = occupied
            doc.available_beds = (doc.total_beds or 0) - occupied
            doc.room_status = "Full" if occupied >= doc.total_beds else "Available"

def on_update_auto_create_alumni_record_on_student_exit(doc, method=None):
    # From Server Script: Auto Create Alumni Record on Student Exit
    if doc.date_of_leaving and doc.date_of_leaving <= frappe.utils.today():
        existing = frappe.db.exists("Alumni Record", {"linked_student": doc.name})
        if not existing:
            alumni = frappe.get_doc({
                "doctype": "Alumni Record",
                "linked_student": doc.name,
                "student_name": doc.student_name,
                "email": doc.student_email_id,
                "graduation_year": frappe.utils.getdate(doc.date_of_leaving).year,
                "alumni_status": "Active"
            })
            alumni.insert(ignore_permissions=True)
            frappe.db.commit()

def on_update_auto_create_hostel_admission_on_approve(doc, method=None):
    # From Server Script: auto-create Hostel Admission on Approve
    if doc.status == "Approved":
        already_exists = frappe.db.exists("Hostel Admission", {"application": doc.name})
        if not already_exists:
            admission = frappe.get_doc({
                "doctype": "Hostel Admission",
                "student": doc.student,
                "student_name": doc.student_name,
                "application": doc.name,
                "hostel": doc.preferred_hostel,
                "room_type": doc.preferred_room_type,
                "academic_year": doc.academic_year,
                "admission_status": "Draft"
            })
            admission.insert(ignore_permissions=True)
    
            frappe.msgprint(
                f"Hostel Admission {admission.name} created. Room Allocation Pending."
            )
    
            warden = frappe.db.get_value("Warden", {"hostel": doc.preferred_hostel}, "employee")
            if warden:
                warden_user = frappe.db.get_value("Employee", warden, "user_id")
                if warden_user:
                    frappe.get_doc({
                        "doctype": "ToDo",
                        "allocated_to": warden_user,
                        "reference_type": "Hostel Admission",
                        "reference_name": admission.name,
                        "description": f"Room Allocation Pending for {doc.student_name} "
                                        f"(Application {doc.name})."
                    }).insert(ignore_permissions=True)

def on_submit_auto_create_sales_invoice_on_submit(doc, method=None):
    # From Server Script: auto-create Sales Invoice on submit
    # Use Create Admission if exists, else Student Applicant
    admission = None
    if doc.student_admission:
        if frappe.db.exists("DocType", "Create Admission"):
            admission = frappe.get_doc("Create Admission", doc.student_admission)
        elif frappe.db.exists("DocType", "Student Applicant"):
            admission = frappe.get_doc("Student Applicant", doc.student_admission)
    
    if not admission:
        return
    
    guardian_email = getattr(admission, 'custom_guardian_email', None) or getattr(admission, 'student_email_id', None)
    first_name = getattr(admission, 'first_name', getattr(admission, 'student_name', 'Guardian'))
    last_name = getattr(admission, 'last_name', '')
    guardian_name = f"{first_name} {last_name or ''}".strip()
    
    customer_name = frappe.db.exists("Customer", {"customer_name": guardian_name})
    if not customer_name:
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": guardian_name,
            "customer_type": "Individual",
            "customer_group": frappe.db.get_single_value("Selling Settings", "customer_group") or "Individual",
            "territory": frappe.db.get_single_value("Selling Settings", "territory") or "All Territories"
        })
        customer.insert(ignore_permissions=True)
        customer_name = customer.name
    
    si_items = []
    for row in (doc.fees or []):
        fee_structure = frappe.get_doc("Fee Structure", row.fee_structure)
        for component in fee_structure.components:
            si_items.append({
                "item_code": component.fees_category,
                "item_name": component.fees_category,
                "qty": 1,
                "rate": component.amount,
                "description": f"Fee for {doc.program} - {row.academic_term or ''}"
            })
    
    if not si_items:
        frappe.throw("No fee components found to create Sales Invoice.")
    
    sales_invoice = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": customer_name,
        "posting_date": frappe.utils.nowdate(),
        "due_date": doc.fees[0].due_date if doc.fees else frappe.utils.nowdate(),
        "items": si_items
    })
    sales_invoice.insert(ignore_permissions=True)
    sales_invoice.submit()
    
    # Try to set sales_invoice on the enrollment
    try:
        frappe.db.set_value("Program Enrollment", doc.name, "custom_sales_invoice", sales_invoice.name)
    except Exception:
        pass
    frappe.msgprint(f"Sales Invoice {sales_invoice.name} created successfully.")

def before_insert_auto_generate_gate_pass_number_on_approval(doc, method=None):
    # From Server Script: auto-generate Gate Pass Number on approval
    old_doc = doc.get_doc_before_save()
    
    if old_doc and old_doc.approval_status != "Approved" and doc.approval_status == "Approved":
        if not doc.gate_pass_number:
            year = frappe.utils.nowdate()[:4]
            count = frappe.db.count("Hostel Leaves", {
                "approval_status": "Approved",
                "gate_pass_number": ["like", f"GP-{year}-%"]
            }) + 1
            gate_pass_number = f"GP-{year}-{str(count).zfill(5)}"
    
            frappe.db.set_value("Hostel Leaves", doc.name, "gate_pass_number", gate_pass_number)
            doc.gate_pass_number = gate_pass_number
    
            frappe.msgprint(f"Gate Pass generated: {gate_pass_number}")

def validate_auto_populate_document_rows_on_new_form(doc, method=None):
    # From Server Script: auto-populate document rows on new form
    if not doc.student_documents:
        default_docs = [
            {"document_name": "Admission Application Form", "is_mandatory": 1, "document_status": "Pending", "purpose": "Student registration"},
            {"document_name": "Birth Certificate", "is_mandatory": 1, "document_status": "Pending", "purpose": "Proof of age"},
            {"document_name": "Passport-size Photographs (Student)", "is_mandatory": 1, "document_status": "Pending", "purpose": "Student ID and records"},
            {"document_name": "Passport-size Photographs (Parents/Guardian)", "is_mandatory": 1, "document_status": "Pending", "purpose": "School records"},
            {"document_name": "Aadhaar Card (Student)", "is_mandatory": 1, "document_status": "Pending", "purpose": "Identity proof"},
            {"document_name": "Aadhaar Card (Parents/Guardian)", "is_mandatory": 0, "document_status": "Pending", "purpose": "Parent identification"},
            {"document_name": "Transfer Certificate (TC)", "is_mandatory": 0, "document_status": "Pending", "purpose": "Previous school transfer"},
            {"document_name": "Previous School Report Card/Marks Card", "is_mandatory": 1, "document_status": "Pending", "purpose": "Academic history"},
            {"document_name": "Residence/Address Proof", "is_mandatory": 1, "document_status": "Pending", "purpose": "Address verification"},
        ]
        for d in default_docs:
            doc.append("student_documents", d)

def before_insert_block_duplicate_applications(doc, method=None):
    # From Server Script: block duplicate applications
    existing = frappe.db.exists("Hostel Application", {
        "student": doc.student,
        "status": ["in", ["Submitted", "Approved"]]
    })
    
    if existing:
        frappe.throw(
            f"Student already has an active application ({existing}) "
            f"with Submitted/Approved status. Cannot create a duplicate."
        )

def on_submit_book_issue___mark_copy_as_issued(doc, method=None):
    # From Server Script: Book Issue - Mark Copy as Issued
    if doc.book_copy:
    
        frappe.db.set_value(
            "Book Copy",
            doc.book_copy,
            "copy_status",
            "Issued"
        )

def before_save_submitted_document_book_issue___validate___set_due_date(doc, method=None):
    # From Server Script: Book Issue - Validate & Set Due Date
    # Get Issue Duration from Library Settings
    issue_days = frappe.db.get_single_value(
        "Library Settings",
        "issue_duration_days"
    ) or 14
    
    # Calculate Due Date
    if doc.issue_date:
        doc.due_date = frappe.utils.add_days(doc.issue_date, issue_days)
    
    # Default Issue Status
    if not doc.issue_status:
        doc.issue_status = "Issued"
    
    # Validate Book Copy Availability
    if doc.book_copy:
        copy_status = frappe.db.get_value(
            "Book Copy",
            doc.book_copy,
            "copy_status"
        )
    
        if copy_status != "Available":
            frappe.throw(
                "The selected Book Copy is no longer available. Please select another copy."
            )

def on_submit_book_return___release_book_copy(doc, method=None):
    # From Server Script: Book Return - Release Book Copy
    # Update Book Copy Status
    if doc.book_copy:
        frappe.db.set_value(
            "Book Copy",
            doc.book_copy,
            "copy_status",
            "Available"
        )
    
    # Update Book Issue Status
    if doc.book_issue:
        frappe.db.set_value(
            "Book Issue",
            doc.book_issue,
            "issue_status",
            "Returned"
        )

def after_save_submitted_document_complaint_assigned_and_to_notify_maintenance(doc, method=None):
    # From Server Script: Complaint assigned and to notify maintenance
    old_doc = doc.get_doc_before_save()
    
    if old_doc and old_doc.assigned_to != doc.assigned_to and doc.assigned_to:
        user = frappe.db.get_value("Employee", doc.assigned_to, "user_id")
    
        if user:
            frappe.get_doc({
                "doctype": "ToDo",
                "allocated_to": user,
                "reference_type": "Grievance Box",
                "reference_name": doc.name,
                "priority": "High" if doc.priority in ("High", "Critical") else "Medium",
                "description": f"Complaint assigned: {doc.category or doc.complaint_type} "
                                f"in Room {doc.hostel_room}. Priority: {doc.priority}."
            }).insert(ignore_permissions=True)
    
    if old_doc and old_doc.status != "Resolved" and doc.status == "Resolved":
        # notify the student their complaint is resolved — via ToDo to Warden
        # since students likely don't have direct system logins (same pattern as earlier phases)
        if doc.warden:
            warden_user = frappe.db.get_value("Warden", doc.warden, "employee")
            warden_user_id = frappe.db.get_value("Employee", warden_user, "user_id") if warden_user else None
            if warden_user_id:
                frappe.get_doc({
                    "doctype": "ToDo",
                    "allocated_to": warden_user_id,
                    "reference_type": "Grievance Box",
                    "reference_name": doc.name,
                    "description": f"Complaint by {doc.student} resolved — please inform student."
                }).insert(ignore_permissions=True)

def after_insert_create_fine_on_book_return(doc, method=None):
    # From Server Script: create_fine_on_book_return
    # Get the linked Book Issue
    book_issue = frappe.get_doc("Book Issue", doc.book_issue)
    
    # Get Fine Per Day from Library Settings
    fine_per_day = frappe.db.get_single_value(
        "Library Settings",
        "fine_per_day"
    ) or 5
    
    # Calculate Overdue Days and Fine
    if book_issue.due_date and doc.return_date:
    
        days_overdue = frappe.utils.date_diff(
            doc.return_date,
            book_issue.due_date
        )
    
        if days_overdue > 0:
            doc.days_overdue = days_overdue
            doc.fine_amount = days_overdue * fine_per_day
        else:
            doc.days_overdue = 0
            doc.fine_amount = 0
    
    else:
        doc.days_overdue = 0
        doc.fine_amount = 0
    
    # Update Book Issue
    frappe.db.set_value(
        "Book Issue",
        doc.book_issue,
        {
            "issue_status": "Returned",
            "return_date": doc.return_date
        }
    )
    
    # Make Book Copy Available
    if book_issue.book_copy:
        frappe.db.set_value(
            "Book Copy",
            book_issue.book_copy,
            "copy_status",
            "Available"
        )
    
    # Create Library Fine only if Fine > 0
    if doc.fine_amount > 0:
    
        existing_fine = frappe.db.exists(
            "Library Fine",
            {
                "book_return": doc.name
            }
        )
    
        if not existing_fine:
    
            fine = frappe.new_doc("Library Fine")
            fine.library_member = doc.library_member
            fine.library_book = doc.library_book
            fine.book_return = doc.name
            fine.amount = doc.fine_amount
            fine.due_date = doc.return_date
            fine.payment_status = "Unpaid"
    
            fine.insert(ignore_permissions=True)

def on_submit_fee_auto_calculation(doc, method=None):
    # From Server Script: fee auto calculation
    if doc.student:
        student = frappe.get_doc("Student", doc.student)
        # Check if student has fee_installments table (from custom field)
        if hasattr(student, 'fee_installments'):
            existing = [r for r in student.fee_installments if r.sales_invoice == doc.name]
            if existing:
                row = existing[0]
            else:
                row = student.append("fee_installments", {})
                row.sales_invoice = doc.name
            row.due_date = doc.due_date
            row.amount = doc.grand_total
            row.outstanding_amount = doc.outstanding_amount
            row.paid_amount = (doc.grand_total or 0) - (doc.outstanding_amount or 0)
            row.status = doc.status
            student.total_fee_payable = sum([r.amount or 0 for r in student.fee_installments])
            student.total_fee_paid = sum([r.paid_amount or 0 for r in student.fee_installments])
            student.fee_balance = student.total_fee_payable - student.total_fee_paid
            student.save(ignore_permissions=True)
            frappe.db.commit()

def on_submit_frees_the_room_if_the_student_check_out(doc, method=None):
    # From Server Script: frees the room if the student check-out
    
    admission = frappe.get_doc("Hostel Admission", doc.hostel_admission)
    admission.admission_status = "Checked Out"
    admission.save(ignore_permissions=True)
    
    room = frappe.get_doc("Hostel Room", admission.hostel_room)
    occupied = frappe.db.count("Hostel Admission", {
        "hostel_room": admission.hostel_room,
        "admission_status": "Checked In"
    })
    room.occupied_beds = occupied
    room.available_beds = (room.total_beds or 0) - occupied
    room.room_status = "Full" if occupied >= room.total_beds else "Available"
    room.save(ignore_permissions=True)

def after_save_submitted_document_handle_the_actual_check_in_transition(doc, method=None):
    # From Server Script: handle the actual check-in transition
    old_doc = doc.get_doc_before_save()
    
    if old_doc and old_doc.admission_status != "Checked In" and doc.admission_status == "Checked In":
    
        # Assign a bed if none already chosen
        if not doc.hostel_bed:
            free_bed = frappe.db.get_value("Hostel Bed", {
                "hostel_room": doc.hostel_room,
                "status": "Available"
            }, "name")
    
            if not free_bed:
                frappe.throw(f"No available bed in Room {doc.hostel_room}. Cannot check in.")
    
            frappe.db.set_value("Hostel Admission", doc.name, "hostel_bed", free_bed)
            doc.hostel_bed = free_bed
    
        bed = frappe.get_doc("Hostel Bed", doc.hostel_bed)
        bed.status = "Occupied"
        bed.student = doc.student
        bed.admission = doc.name
        bed.save(ignore_permissions=True)
    
        # Set check-in timestamp
        frappe.db.set_value("Hostel Admission", doc.name, {
            "check_in_date": frappe.utils.today(),
            "check_in_time": frappe.utils.nowtime()
        })
    
        # Sync room occupancy
        room = frappe.get_doc("Hostel Room", doc.hostel_room)
        occupied = frappe.db.count("Hostel Admission", {
            "hostel_room": doc.hostel_room,
            "admission_status": "Checked In"
        })
        room.occupied_beds = occupied
        room.available_beds = (room.total_beds or 0) - occupied
        room.room_status = "Full" if occupied >= room.total_beds else "Available"
        room.save(ignore_permissions=True)
    
        frappe.msgprint(f"{doc.student_name} checked in — Bed {bed.bed_number} assigned.")

def validate_library_fine___process_payment(doc, method=None):
    # From Server Script: Library Fine - Process Payment
    # Prevent changing a paid fine
    if not doc.is_new():
    
        old_doc = frappe.get_doc("Library Fine", doc.name)
    
        if old_doc.payment_status == "Paid":
            frappe.throw("This fine has already been paid and cannot be modified.")
    
    # Set Payment Date automatically
    if doc.payment_status == "Paid" and not doc.payment_date:
        doc.payment_date = frappe.utils.today()

def after_save_submitted_document_notification_script(doc, method=None):
    # From Server Script: Notification Script
    import frappe
    
    if doc.publish:
    
        frappe.msgprint(
            f"'{doc.title}' has been published successfully."
        )

def validate_prevent_duplicate_active_assignments(doc, method=None):
    # From Server Script: Prevent Duplicate Active Assignments
    if doc.is_active and not doc.transport_route:
        frappe.throw("Please select a Transport Route before activating the assignment.")
    
    existing = frappe.get_all(
        "Student Transport Assignment",
        filters={
            "student": doc.student,
            "is_active": 1,
            "name": ["!=", doc.name]
        },
        fields=["name", "student_name"],
        limit=1
    )
    
    if existing:
        assignment = existing[0]
        frappe.throw(
            f"{assignment.student_name} already has an active Transport Assignment ({assignment.name})."
        )

def before_insert_prevent_duplicate_certificates(doc, method=None):
    # From Server Script: Prevent Duplicate Certificates
    existing = frappe.db.exists(
        "Student Certificate",
        {
            "student": doc.student,
            "template": doc.template
        }
    )
    
    if existing:
        frappe.throw("This certificate has already been generated for this student.")

def on_submit_student_event_celebration(doc, method=None):
    # From Server Script: Student event Celebration
    if doc.student_group:
        # Step 1: Get students from the selected Student Group
        student_group = frappe.get_doc("Student Group", doc.student_group)
        student_ids = [s.student for s in student_group.students]
    
        # Step 2: Find Guardians linked to those students
        guardian_emails = set()
        guardians = frappe.get_all("Guardian", fields=["name", "email_address"])
        for guardian in guardians:
            guardian_doc = frappe.get_doc("Guardian", guardian.name)
            for gs in guardian_doc.students:
                if gs.student in student_ids and guardian_doc.email_address:
                    guardian_emails.add(guardian_doc.email_address)
    
        # Step 3: Compose email
        subject = f"Event from Bizaxl school"
        message = f"""<div>
            <h2>Parent Invitation</h2>
            <h3>{doc.subject}</h3>
            <p>Dear Parent,</p>
            <p>You are invited to attend an important event scheduled for your child enrolled in group <strong>{doc.student_group}</strong>.</p>
            <table>
                <tr><td>Date:</td><td>{doc.date}</td></tr>
                <tr><td>Time:</td><td>{doc.time}</td></tr>
                <tr><td>Venue:</td><td>{doc.venue}</td></tr>
            </table>
            <h4>Agenda:</h4>
            <p>{doc.agenda}</p>
            <p>We look forward to seeing you there!</p>
            <p>Let's make this event memorable together!</p>
        </div>"""
    
        # Step 4: Send email to all unique guardian emails
        if guardian_emails:
            frappe.sendmail(
                recipients=list(guardian_emails),
                subject=subject,
                message=message
            )

def before_submit_sync_data_when_enrollment_is_submitted(doc, method=None):
    # From Server Script: sync data when enrollment is submitted
    if not doc.custom_student:
        matched_student = None
        email = None
    
        if doc.student_admission and "@" in doc.student_admission:
            email = doc.student_admission
    
        if not email and doc.student_admission:
            # Try Create Admission or Student Applicant
            if frappe.db.exists("DocType", "Create Admission"):
                if frappe.db.exists("Create Admission", doc.student_admission):
                    admission_dict = frappe.get_doc("Create Admission", doc.student_admission).as_dict()
                    email = admission_dict.get("student_email_id") or admission_dict.get("email")
            elif frappe.db.exists("DocType", "Student Applicant"):
                if frappe.db.exists("Student Applicant", doc.student_admission):
                    admission_dict = frappe.get_doc("Student Applicant", doc.student_admission).as_dict()
                    email = admission_dict.get("student_email_id") or admission_dict.get("email")
    
        if email:
            matched_student = frappe.db.get_value("Student", {"student_email_id": email}, "name")
    
        if not matched_student and doc.student_name:
            cleaned_name = doc.student_name.strip()
            matched_student = frappe.db.get_value("Student", {"student_name": cleaned_name}, "name")
    
        if not matched_student:
            full_name = (doc.student_name or "Unknown").strip()
            name_parts = full_name.split(" ")
            first = name_parts[0] if len(name_parts) > 0 else full_name
            last = name_parts[-1] if len(name_parts) > 1 else ""
    
            new_student = frappe.get_doc({
                "doctype": "Student",
                "first_name": first,
                "last_name": last,
                "student_name": full_name,
                "student_email_id": email,
                "enabled": 1
            })
            new_student.insert(ignore_permissions=True)
            matched_student = new_student.name
    
        doc.custom_student = matched_student

def validate_to_keep_room_display_updated_automatically(doc, method=None):
    # From Server Script: to keep room_display updated automatically
    available = (doc.total_beds or 0) - (doc.occupied_beds or 0)
    
    if doc.room_status == "Full":
        doc.room_display = f"{doc.room_number} — Full"
    elif doc.room_status == "Maintenance":
        doc.room_display = f"{doc.room_number} — Maintenance"
    else:
        bed_word = "Bed" if available == 1 else "Beds"
        doc.room_display = f"{doc.room_number} — {available} {bed_word} Available"

def on_submit_to_update_room_occupancy(doc, method=None):
    # From Server Script: to update room occupancy
    
    room = frappe.get_doc("Hostel Room", doc.hostel_room)
    
    occupied = frappe.db.count("Hostel Admission", {
        "hostel_room": doc.hostel_room,
        "admission_status": "Checked In"
    })
    
    room.occupied_beds = occupied
    room.available_beds = (room.total_beds or 0) - occupied
    room.room_status = "Full" if occupied >= room.total_beds else "Available"
    room.save(ignore_permissions=True)

def validate_validate_hall_capacity(doc, method=None):
    # From Server Script: Validate Hall Capacity
    if doc.exam_hall:
        try:
            capacity = frappe.db.get_value("Exam Hall", doc.exam_hall, "capacity")
        except Exception:
            capacity = None
    
        if capacity:
            student_count = len(doc.students or [])
            if student_count > capacity:
                frappe.throw(
                    "Cannot allocate {0} students to {1}. Hall capacity is only {2}.".format(
                        student_count, doc.exam_hall, capacity
                    )
                )
