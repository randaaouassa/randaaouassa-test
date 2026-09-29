from odoo import models, fields, api


class Equipment(models.Model):
    """A physical item owned by the company."""
    _name = 'equipment.equipment'
    _description = 'Company Equipment'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --- Basic info ---
    name = fields.Char(required=True, index=True, tracking=True)
    reference = fields.Char(index=True, copy=False, tracking=True)
    category_id = fields.Many2one('equipment.category', index=True, tracking=True)

    # --- Lifecycle ---
    state = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired'),
    ], default='available', required=True, index=True, tracking=True)

    active = fields.Boolean(default=True)

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
        """Enforce unique reference (ignoring empty values) at DB level."""
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_equipment_reference
            ON equipment_equipment (reference)
            WHERE reference IS NOT NULL AND reference != '';
        """)

    # --- ORM overrides ---
    def name_get(self):
        """Display equipment as [REF] Name in dropdowns and links."""
        result = []
        for rec in self:
            label = f"[{rec.reference}] {rec.name}" if rec.reference else rec.name
            result.append((rec.id, label))
        return result

    # --- Computes ---
    @api.depends('assignment_ids.state')
    def _compute_current_assignment(self):
        """Find the active assignment for each equipment in one query."""
        Assignment = self.env['equipment.assignment']
        active = Assignment.search([
            ('equipment_id', 'in', self.ids),
            ('state', '=', 'active'),
        ])
        by_equipment = {a.equipment_id.id: a for a in active}
        for rec in self:
            rec.current_assignment_id = by_equipment.get(rec.id)

    @api.depends('assignment_ids')
    def _compute_assignment_count(self):
        """Count assignments per equipment using a single grouped query."""
        groups = self.env['equipment.assignment'].read_group(
            [('equipment_id', 'in', self.ids)],
            ['equipment_id'],
            ['equipment_id'],
        )
        counts = {g['equipment_id'][0]: g['equipment_id_count'] for g in groups}
        for rec in self:
            rec.assignment_count = counts.get(rec.id, 0)

    # --- Actions ---
    def action_view_assignments(self):
        """Open the filtered assignment list for this equipment."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignments',
            'res_model': 'equipment.assignment',
            'view_mode': 'tree,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }