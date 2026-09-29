from odoo import models, fields, api


class Equipment(models.Model):
    """A physical item owned by the company."""
    _name = 'equipment.equipment'
    _description = 'Company Equipment'
    _order = 'name'

    # --- Basic info ---
    name = fields.Char(required=True, index=True)
    reference = fields.Char(index=True)
    category_id = fields.Many2one('equipment.category', index=True)

    # --- Lifecycle ---
    state = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired'),
    ], default='available', required=True, index=True)

    # --- Relations ---
    current_assignment_id = fields.Many2one(
        'equipment.assignment',
        compute='_compute_current_assignment', store=True, index=True,
    )
    assignment_ids = fields.One2many(
        'equipment.assignment', 'equipment_id', string='History',
    )
    assignment_count = fields.Integer(compute='_compute_assignment_count')

    # --- SQL ---
    def init(self):
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_equipment_reference
            ON equipment_equipment (reference)
            WHERE reference IS NOT NULL AND reference != '';
        """)

    # --- Computes ---
    @api.depends('assignment_ids.state')
    def _compute_current_assignment(self):
        for rec in self:
            rec.current_assignment_id = rec.assignment_ids.filtered(
                lambda a: a.state == 'active'
            )[:1]

    @api.depends('assignment_ids')
    def _compute_assignment_count(self):
        groups = self.env['equipment.assignment'].read_group(
            [('equipment_id', 'in', self.ids)],
            ['equipment_id'],
            ['equipment_id'],
        )
        counts = {g['equipment_id'][0]: g['equipment_id_count'] for g in groups}
        for rec in self:
            rec.assignment_count = counts.get(rec.id, 0)