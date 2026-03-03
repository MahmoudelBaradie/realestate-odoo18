# Real Estate Development & Property Management ERP (Odoo 18 Community)

This repository now contains a full modular custom implementation for a real estate ERP stack:

- `real_estate_security`
- `real_estate_core`
- `real_estate_accounting_bridge`
- `real_estate_land`
- `real_estate_units`
- `real_estate_project_wip`
- `real_estate_sales`
- `real_estate_rental`
- `real_estate_procurement`
- `real_estate_property`
- `real_estate_reports`

## Highlights

- Configurable accounting accounts from settings (no hardcoded account ids).
- Automatic accounting entries for land capitalization, project close, sales, rentals, and contractor progress billing.
- Analytic account creation and linkage for land and project cost tracking.
- Unit lifecycle states: available, reserved, sold, rented.
- Role-oriented security groups for accountant, project manager, sales manager, and general manager.
- Basic reporting entry point for analytic-driven budget vs actual analysis.
