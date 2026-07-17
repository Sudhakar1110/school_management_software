# Copyright (c) 2026, School Management and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, today, getdate

class AssetRegister(Document):
    """Track school assets through their lifecycle with depreciation"""
    
    def before_save(self):
        """Auto-calculate current value based on depreciation"""
        if self.purchase_cost and self.depreciation_method != "No Depreciation" and self.useful_life_years:
            years_held = date_diff(today(), getdate(self.purchase_date)) / 365.0
            
            if years_held > 0:
                if self.depreciation_method == "Straight Line":
                    annual_dep = (self.purchase_cost - (self.salvage_value or 0)) / self.useful_life_years
                    total_dep = annual_dep * min(years_held, self.useful_life_years)
                    self.current_value = max(self.purchase_cost - total_dep, self.salvage_value or 0)
                elif self.depreciation_method == "Written Down Value":
                    rate = 1 - ( (self.salvage_value or 0) / self.purchase_cost ) ** (1/self.useful_life_years)
                    self.current_value = self.purchase_cost * (1 - rate) ** min(years_held, self.useful_life_years)
                    self.current_value = max(self.current_value, self.salvage_value or 0)
            else:
                self.current_value = self.purchase_cost
        elif self.purchase_cost:
            self.current_value = self.purchase_cost