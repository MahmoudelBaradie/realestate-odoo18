from odoo import _, fields, models
from odoo.exceptions import UserError


class RealEstateSale(models.Model):
    _name = 'real.estate.sale'
    _description = 'Unit Sale Contract'
    _inherit = ['mail.thread', 'real.estate.accounting.mixin']

    name = fields.Char(required=True, copy=False, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', required=True)
    unit_id = fields.Many2one('real.estate.unit', required=True)
    contract_value = fields.Monetary(required=True)
    cost_value = fields.Monetary(related='unit_id.cost')
    installment_count = fields.Integer(default=1)
    delivery_status = fields.Selection([('pending', 'Pending'), ('delivered', 'Delivered')], default='pending')
    state = fields.Selection([('draft', 'Draft'), ('reserved', 'Reserved'), ('sold', 'Sold')], default='draft')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    margin = fields.Monetary(compute='_compute_margin')

    def _compute_margin(self):
        for rec in self:
            rec.margin = rec.contract_value - rec.cost_value

    def action_reserve(self):
        for rec in self:
            rec.unit_id.status = 'reserved'
            rec.state = 'reserved'

    def action_confirm_sale(self):
        for rec in self:
            if rec.unit_id.status not in ('reserved', 'available'):
                raise UserError(_('Unit must be available or reserved before sale.'))
            revenue = rec._get_required_account('real_estate_core.sales_revenue_account_id')
            receivable = rec.partner_id.property_account_receivable_id
            if not receivable:
                raise UserError(_('Customer receivable account is required.'))
            rec._post_simple_entry(receivable, revenue, rec.contract_value, rec.partner_id, rec.name)

            cos = rec._get_required_account('real_estate_core.cost_of_sales_account_id')
            inventory = rec._get_required_account('real_estate_core.inventory_account_id')
            rec._post_simple_entry(cos, inventory, rec.cost_value, rec.partner_id, f'{rec.name} COS')
            rec.unit_id.status = 'sold'
            rec.state = 'sold'
