import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist()
def update_vehicle_location(vehicle, latitude, longitude, speed=None, heading=None, status="On Route", battery_level=100):
    """API endpoint for GPS devices to push location data"""
    if not frappe.db.exists("Transport Vehicle", vehicle):
        frappe.throw(_("Vehicle {0} not found").format(vehicle))
    
    log = frappe.get_doc({
        "doctype": "Vehicle GPS Tracking Log",
        "vehicle": vehicle,
        "latitude": latitude,
        "longitude": longitude,
        "speed": speed or 0,
        "heading": heading or 0,
        "status": status,
        "timestamp": now_datetime(),
        "battery_level": battery_level,
        "is_processed": 0
    })
    log.insert(ignore_permissions=True)
    
    # Update the vehicle's last known location
    frappe.db.set_value("Transport Vehicle", vehicle, {
        "last_latitude": latitude,
        "last_longitude": longitude,
        "last_location_update": now_datetime()
    })
    
    return {"success": True, "log_id": log.name}


@frappe.whitelist()
def get_vehicle_location(vehicle):
    """Get the latest location for a vehicle"""
    latest = frappe.get_all("Vehicle GPS Tracking Log",
        filters={"vehicle": vehicle},
        fields=["latitude", "longitude", "speed", "heading", "status", "timestamp", "battery_level"],
        order_by="timestamp desc",
        limit=1
    )
    
    if not latest:
        return {"available": False, "message": _("No location data available for this vehicle")}
    
    return {"available": True, "data": latest[0]}


@frappe.whitelist()
def get_all_vehicles_status():
    """Get current status of all GPS-equipped vehicles"""
    vehicles = frappe.get_all("Transport Vehicle",
        filters={"gps_installed": 1},
        fields=["name", "vehicle_name", "vehicle_type", "driver_name", "last_latitude", "last_longitude", "last_location_update"]
    )
    
    result = []
    for v in vehicles:
        # Get latest tracking log
        latest = frappe.get_all("Vehicle GPS Tracking Log",
            filters={"vehicle": v.name},
            fields=["status", "speed", "timestamp"],
            order_by="timestamp desc",
            limit=1
        )
        
        result.append({
            "name": v.name,
            "vehicle_name": v.vehicle_name or v.name,
            "vehicle_type": v.vehicle_type,
            "driver_name": v.driver_name or "Not assigned",
            "latitude": v.last_latitude,
            "longitude": v.last_longitude,
            "last_update": str(v.last_location_update or ""),
            "current_status": latest[0].status if latest else "Offline",
            "speed": latest[0].speed if latest else 0,
            "last_timestamp": str(latest[0].timestamp) if latest else ""
        })
    
    return result


@frappe.whitelist(allow_guest=True)
def get_public_vehicle_location(vehicle_id):
    """Public endpoint for parents to track school bus location"""
    vehicle = frappe.db.get_value("Transport Vehicle", vehicle_id, 
        ["name", "vehicle_name", "gps_installed", "last_latitude", "last_longitude", "last_location_update"],
        as_dict=1
    )
    
    if not vehicle or not vehicle.gps_installed:
        return {"available": False, "message": _("Tracking not available for this vehicle")}
    
    latest = frappe.get_all("Vehicle GPS Tracking Log",
        filters={"vehicle": vehicle_id},
        fields=["latitude", "longitude", "speed", "timestamp", "status"],
        order_by="timestamp desc",
        limit=1
    )
    
    return {
        "available": True,
        "vehicle_name": vehicle.vehicle_name,
        "current_location": latest[0] if latest else None,
        "last_update": str(vehicle.last_location_update or "")
    }
