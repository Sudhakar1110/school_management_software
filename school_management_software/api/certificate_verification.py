import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def verify_certificate(certificate_id):
    """Public API for certificate verification"""
    if not certificate_id:
        return {"valid": False, "message": "Certificate ID is required"}
    
    if not frappe.db.exists("Student Certificate", certificate_id):
        return {"valid": False, "message": _("Certificate not found")}
    
    cert = frappe.get_doc("Student Certificate", certificate_id)
    
    # Get student info
    student_name = cert.student_name if hasattr(cert, 'student_name') else ""
    
    # Get template/info
    template_name = cert.template if hasattr(cert, 'template') else ""
    
    # Get issuer info
    issued_by = frappe.db.get_value("User", cert.generated_by, "full_name") if hasattr(cert, 'generated_by') else ""
    
    return {
        "valid": True,
        "student_name": student_name,
        "certificate_type": template_name,
        "issued_on": str(cert.generated_on) if hasattr(cert, 'generated_on') else "",
        "issued_by": issued_by or "",
        "status": cert.status if hasattr(cert, 'status') else "",
        "certificate_url": cert.certificate_pdf if hasattr(cert, 'certificate_pdf') else ""
    }


@frappe.whitelist()
def generate_qr_for_certificate(certificate_id):
    """Generate QR code for certificate verification"""
    if not certificate_id:
        frappe.throw(_("Certificate ID is required"))
    
    try:
        import qrcode
        from io import BytesIO
        import base64
        
        verification_url = "{0}/api/method/school_management_software.api.certificate_verification.verify_certificate?certificate_id={1}".format(
            frappe.utils.get_url(),
            certificate_id
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(verification_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "success": True,
            "qr_base64": "data:image/png;base64,{0}".format(qr_base64),
            "verification_url": verification_url
        }
    except ImportError:
        frappe.throw(_("qrcode library is required. Install with: pip install qrcode"))
    except Exception as e:
        frappe.log_error(title="QR Generation Error", message=str(e))
        frappe.throw(_("Failed to generate QR code: {0}").format(str(e)))
