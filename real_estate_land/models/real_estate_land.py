from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class RealEstateLand(models.Model):
    _name = 'real.estate.land'
    _description = 'Land Acquisition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'real.estate.accounting.mixin']

    name = fields.Char(default=lambda self: _('New'), copy=False, readonly=True)
    location = fields.Char(required=True)
    area = fields.Float(required=True)
    area_uom = fields.Selection([
        ('feddan', 'Feddan'),
        ('qirat', 'Qirat'),
        ('sqm', 'Square Meter'),
    ], default='sqm', required=True)
    area_sqm = fields.Float(compute='_compute_area_sqm', store=True)
    purchase_price = fields.Monetary(required=True)
    additional_cost = fields.Monetary()
    total_land_cost = fields.Monetary(compute='_compute_total_cost', store=True)
    payment_method = fields.Selection([('cash', 'Cash'), ('bank', 'Bank'), ('payable', 'Payable')], default='payable')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('capitalized', 'Capitalized'),
    ], default='draft', tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', readonly=True)
    move_id = fields.Many2one('account.move', readonly=True)

    @api.depends('area', 'area_uom')
    def _compute_area_sqm(self):
        factors = {'sqm': 1.0, 'qirat': 175.0, 'feddan': 4200.0}
        for rec in self:
            rec.area_sqm = rec.area * factors.get(rec.area_uom, 1.0)

    @api.depends('purchase_price', 'additional_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_land_cost = rec.purchase_price + rec.additional_cost

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('real.estate.land') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        if any(rec.state == 'capitalized' for rec in self):
            raise UserError(_('Capitalized land records cannot be modified.'))
        return super().write(vals)

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            analytic = self.env['account.analytic.account'].create({'name': rec.name, 'company_id': rec.company_id.id})
            rec.analytic_account_id = analytic
            debit = rec._get_required_account('real_estate_core.land_asset_account_id')
            credit_map = {
                'cash': rec._get_required_account('real_estate_core.cash_bank_account_id'),
                'bank': rec._get_required_account('real_estate_core.cash_bank_account_id'),
                'payable': rec.partner_id.property_account_payable_id,
            }
            credit = credit_map.get(rec.payment_method)
            if not credit:
                raise ValidationError(_('Please set vendor payable account or company payment account.'))
            rec.move_id = rec._post_simple_entry(debit, credit, rec.total_land_cost, rec.partner_id, rec.name, analytic)
            rec.state = 'confirmed'

    def action_capitalize(self):
        self.write({'state': 'capitalized'})
