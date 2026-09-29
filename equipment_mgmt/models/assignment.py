from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Assignment(models.Model):
    """A record of equipment given to an employee (kept forever as history)."""
    _name = 'equipment.assignment'
    _description = 'Equipment Assignment'
    _order = 'date_start desc'
    _rec_name = 'equipment_id'

    # --- Relations ---
    equipment_id = fields.Many2one(
        'equipment.equipment', required=True,
        ondelete='cascade', index=True,
    )
    employee_id = fields.Many2one(
        'hr.employee', required=True,
        ondelete='restrict', index=True,
    )

    # --- Dates ---
    date_start = fields.Datetime(
        default=fields.Datetime.now, required=True, index=True,
    )
    date_end = fields.Datetime()

    # --- Status ---
    state = fields.Selection([
        ('active', 'Active'),
        ('returned', 'Returned'),
    ], default='active', required=True, index=True)

    # --- Extra ---
    notes = fields.Text()

    # --- SQL ---
    def init(self):
        """Enforce one active assignment per equipment at DB level."""
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_active_per_equipment
            ON equipment_assignment (equipment_id)
            WHERE state = 'active';
        """)

    # --- ORM overrides ---
    @api.model_create_multi
    def create(self, vals_list):
        """Create assignments and sync the equipment state."""
        records = super().create(vals_list)
        records._sync_equipment_state()
        return records

    def write(self, vals):
        """Sync equipment state when the assignment changes."""
        res = super().write(vals)
        if 'state' in vals or 'equipment_id' in vals:
            self._sync_equipment_state()
        return res

    # --- Constraints ---
    @api.constrains('equipment_id', 'state')
    def _check_single_active(self):
        """Reject a second active assignment on the same equipment."""
        for rec in self:
            if rec.state != 'active':
                continue
            if self.search_count([
                ('equipment_id', '=', rec.equipment_id.id),
                ('state', '=', 'active'),
                ('id', '!=', rec.id),
            ]):
                raise ValidationError(
                    "This equipment already has an active assignment."
                )

    # --- Actions ---
    def action_return(self):
        """Close the assignment: set date_end and state=returned."""
        for rec in self:
            if rec.state != 'active':
                continue
            rec.write({
                'state': 'returned',
                'date_end': rec.date_end or fields.Datetime.now(),
            })

    # --- Helpers ---
    def _sync_equipment_state(self):
        """Flip equipment state to assigned/available based on active assignments."""
        for equipment in self.mapped('equipment_id'):
            has_active = bool(equipment.assignment_ids.filtered(
                lambda a: a.state == 'active'
            ))
            if has_active and equipment.state == 'available':
                equipment.state = 'assigned'
            elif not has_active and equipment.state == 'assigned':
                equipment.state = 'available'