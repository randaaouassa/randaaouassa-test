"""
Seed demo data for screenshots.

Usage:
    MSYS_NO_PATHCONV=1 docker exec -i odoo odoo shell -d equipment2 \
      --db_host=db --db_user=odoo --db_password=odoo \
      < equipment_mgmt/scripts/seed_demo.py
"""

# --- Categories ---
categories = {}
for name in ['Laptop', 'Phone', 'Tool', 'Accessory', 'Monitor']:
    categories[name] = env['equipment.category'].create({'name': name})

# --- Employees ---
employees = {}
for name in ['Alice Martin', 'Bob Chen', 'Clara Doe', 'David Kim', 'Eva Rossi']:
    employees[name] = env['hr.employee'].create({'name': name})

# --- Equipment ---
equipment_data = [
    ('Dell XPS 15', 'LAP-001', 'Laptop'),
    ('MacBook Pro 14', 'LAP-002', 'Laptop'),
    ('ThinkPad X1', 'LAP-003', 'Laptop'),
    ('iPhone 14', 'PHN-001', 'Phone'),
    ('Samsung Galaxy S23', 'PHN-002', 'Phone'),
    ('Google Pixel 8', 'PHN-003', 'Phone'),
    ('Cordless Drill', 'TOL-001', 'Tool'),
    ('Torque Wrench', 'TOL-002', 'Tool'),
    ('LG UltraWide 34"', 'MON-001', 'Monitor'),
    ('Dell 27" 4K', 'MON-002', 'Monitor'),
    ('Logitech MX Master', 'ACC-001', 'Accessory'),
    ('Sony WH-1000XM5', 'ACC-002', 'Accessory'),
]

equipment = []
for name, ref, cat in equipment_data:
    equipment.append(env['equipment.equipment'].create({
        'name': name,
        'reference': ref,
        'category_id': categories[cat].id,
    }))

# --- Assignments ---
# Active assignments
env['equipment.assignment'].create({
    'equipment_id': equipment[0].id,
    'employee_id': employees['Alice Martin'].id,
})
env['equipment.assignment'].create({
    'equipment_id': equipment[3].id,
    'employee_id': employees['Bob Chen'].id,
})
env['equipment.assignment'].create({
    'equipment_id': equipment[6].id,
    'employee_id': employees['Clara Doe'].id,
})

# Past (returned) assignments
past = env['equipment.assignment'].create({
    'equipment_id': equipment[1].id,
    'employee_id': employees['David Kim'].id,
})
past.action_return()

past2 = env['equipment.assignment'].create({
    'equipment_id': equipment[4].id,
    'employee_id': employees['Eva Rossi'].id,
})
past2.action_return()

env.cr.commit()
print(f"\n✅ Seeded: {len(categories)} categories, {len(employees)} employees, {len(equipment)} equipment, 5 assignments")