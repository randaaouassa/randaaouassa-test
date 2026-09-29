from odoo import models, fields


class EquipmentCategory(models.Model):
    """Lookup table for equipment categories (Laptop, Phone, Tool...)."""
    _name = 'equipment.category'
    _description = 'Equipment Category'
    _order = 'name'

    # --- Basic info ---
    name = fields.Char(required=True, index=True)