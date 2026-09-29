from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAssignment(TransactionCase):

    def setUp(self):
        super().setUp()
        self.equipment = self.env['equipment.equipment'].create({
            'name': 'Test Laptop',
        })
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
        })

    def test_create_assignment_sets_equipment_assigned(self):
        self.env['equipment.assignment'].create({
            'equipment_id': self.equipment.id,
            'employee_id': self.employee.id,
        })
        self.assertEqual(self.equipment.state, 'assigned')

    def test_return_assignment_frees_equipment(self):
        assignment = self.env['equipment.assignment'].create({
            'equipment_id': self.equipment.id,
            'employee_id': self.employee.id,
        })
        assignment.action_return()
        self.assertEqual(assignment.state, 'returned')
        self.assertEqual(self.equipment.state, 'available')
        self.assertTrue(assignment.date_end)

    def test_no_double_active_assignment(self):
        self.env['equipment.assignment'].create({
            'equipment_id': self.equipment.id,
            'employee_id': self.employee.id,
        })
        with self.assertRaises(Exception):
            self.env['equipment.assignment'].create({
                'equipment_id': self.equipment.id,
                'employee_id': self.employee.id,
            })
            self.env.flush_all()

    def test_current_assignment_computed(self):
        assignment = self.env['equipment.assignment'].create({
            'equipment_id': self.equipment.id,
            'employee_id': self.employee.id,
        })
        self.assertEqual(self.equipment.current_assignment_id, assignment)

    def test_unique_reference(self):
        self.env['equipment.equipment'].create({
            'name': 'A', 'reference': 'REF-001',
        })
        with self.assertRaises(Exception):
            self.env['equipment.equipment'].create({
                'name': 'B', 'reference': 'REF-001',
            })
            self.env.flush_all()