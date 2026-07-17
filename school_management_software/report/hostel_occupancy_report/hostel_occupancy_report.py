# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    """Hostel Occupancy Report - Rooms, beds, occupancy percentage"""
    columns = [
        {"label": "Hostel", "fieldname": "hostel", "fieldtype": "Data", "width": 150},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "Room", "fieldname": "room", "fieldtype": "Data", "width": 100},
        {"label": "Room Type", "fieldname": "room_type", "fieldtype": "Data", "width": 120},
        {"label": "Total Beds", "fieldname": "total_beds", "fieldtype": "Int", "width": 100},
        {"label": "Occupied", "fieldname": "occupied", "fieldtype": "Int", "width": 100},
        {"label": "Available", "fieldname": "available", "fieldtype": "Int", "width": 100},
        {"label": "Occupancy %", "fieldname": "occupancy_pct", "fieldtype": "Percent", "width": 100}
    ]
    data = frappe.db.sql("""
        SELECT hr.hostel, hr.hostel_block AS block, hr.room_number AS room,
               hr.room_type, hr.total_beds, hr.occupied_beds AS occupied,
               hr.available_beds AS available,
               CASE WHEN hr.total_beds > 0
                    THEN ROUND(hr.occupied_beds * 100.0 / hr.total_beds, 1)
                    ELSE 0 END AS occupancy_pct
        FROM `tabHostel Room` hr
        ORDER BY hr.hostel, hr.hostel_block, hr.room_number
    """, as_dict=True)
    return columns, data
