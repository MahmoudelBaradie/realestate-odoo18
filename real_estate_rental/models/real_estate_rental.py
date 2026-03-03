from dateutil.relativedelta import relativedelta
from odoo import fields, models


class RealEstateRentalContract(models.Model):
    _name = 'real.estate.rental.contract'
    _description = 'Rental Contract'
    _inherit = ['mail.thread', 'real.estate.accounting.mixin']

    name = fields.Char(required=True)
    tenant_id = fields.Many2one('res.partner', required=True)
    unit_id = fields.Many2one('real.estate.unit', required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    rent_value = fields.Monetary(required=True)
    billing_cycle = fields.Selection([('monthly', 'Monthly'), ('quarterly', 'Quarterly')], default='monthly')
    security_deposit = fields.Monetary()
    next_invoice_date = fields.Date()
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('closed', 'Closed')], default='draft')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    def action_activate(self):
        for rec in self:
            rec.unit_id.status = 'rented'
            rec.next_invoice_date = rec.date_start
            rec.state = 'active'
            if rec.security_deposit:
                payable = rec._get_required_account('real_estate_core.security_deposit_account_id')
                receivable = rec.tenant_id.property_account_receivable_id
                rec._post_simple_entry(receivable, payable, rec.security_deposit, rec.tenant_id, f'{rec.name} Deposit')

    def _create_rent_entry(self):
        for rec in self.filtered(lambda c: c.state == 'active' and c.next_invoice_date):
            revenue = rec._get_required_account('real_estate_core.rental_revenue_account_id')
            receivable = rec.tenant_id.property_account_receivable_id
            rec._post_simple_entry(receivable, revenue, rec.rent_value, rec.tenant_id, f'{rec.name} Rent')
            months = 1 if rec.billing_cycle == 'monthly' else 3
            rec.next_invoice_date = rec.next_invoice_date + relativedelta(months=months)

    def cron_generate_rent_entries(self):
        today = fields.Date.today()
        contracts = self.search([('state', '=', 'active'), ('next_invoice_date', '<=', today)])
        contracts._create_rent_entry()
