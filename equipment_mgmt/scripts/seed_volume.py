"""
Seed volume data for performance testing.

Usage:
    docker exec odoo odoo shell -d equipment --db_host=db \
      --db_user=odoo --db_password=odoo < scripts/seed_volume.py
"""
import time
import logging

_logger = logging.getLogger(__name__)

COUNT = 10000

# --- Seed equipment ---
t0 = time.time()
vals = [
    {'name': f'Equipment {i}', 'reference': f'REF-{i:05d}'}
    for i in range(COUNT)
]
env['equipment.equipment'].create(vals)
env.cr.commit()
create_time = time.time() - t0

# --- Measure read ---
t0 = time.time()
records = env['equipment.equipment'].search([], limit=80)
records.read(['name', 'reference', 'state'])
read_time = time.time() - t0

# --- Measure filtered read ---
t0 = time.time()
env['equipment.equipment'].search([('state', '=', 'available')], limit=80)
filter_time = time.time() - t0

print(f"\n=== VOLUME TEST ===")
print(f"Created:  {COUNT} equipment in {create_time:.2f}s")
print(f"Read 80:  {read_time*1000:.1f} ms")
print(f"Filter:   {filter_time*1000:.1f} ms")