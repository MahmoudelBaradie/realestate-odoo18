from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RealEstateProject(models.Model):
    _name = 'real.estate.project'
    _description = 'Real Estate Project WIP'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'real.estate.accounting.mixin']

    name = fields.Char(required=True)
    land_id = fields.Many2one('real.estate.land', required=True)
    estimated_budget = fields.Monetary(required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    analytic_account_id = fields.Many2one('account.analytic.account', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('active', 'In Progress'), ('closed', 'Closed')], default='draft', tracking=True)
    completion_option = fields.Selection([('sale', 'Convert to Inventory Units'), ('rental', 'Convert to Investment Property')])
    actual_cost = fields.Monetary(compute='_compute_actual_cost')
    variance = fields.Monetary(compute='_compute_variance')

    @api.depends('analytic_account_id')
    def _compute_actual_cost(self):
        for rec in self:
            if not rec.analytic_account_id:
                rec.actual_cost = 0.0
                continue
            lines = self.env['account.move.line'].search([
                ('analytic_distribution', '!=', False),
                ('move_id.state', '=', 'posted'),
            ])
            rec.actual_cost = sum(
                line.debit - line.credit
                for line in lines
                if str(rec.analytic_account_id.id) in (line.analytic_distribution or {})
            )

    @api.depends('estimated_budget', 'actual_cost')
    def _compute_variance(self):
        for rec in self:
            rec.variance = rec.estimated_budget - rec.actual_cost

    def action_start(self):
        for rec in self:
            rec.analytic_account_id = self.env['account.analytic.account'].create({
                'name': rec.name,
                'company_id': rec.company_id.id,
            })
            rec.state = 'active'

    def action_close(self):
        for rec in self:
            if not rec.completion_option:
                raise UserError(_('Choose completion option before closing.'))
            amount = rec.actual_cost
            if rec.completion_option == 'sale':
                debit = rec._get_required_account('real_estate_core.inventory_account_id')
            else:
                debit = rec._get_required_account('real_estate_core.investment_property_account_id')
            credit = rec._get_required_account('real_estate_core.wip_account_id')
            rec._post_simple_entry(debit, credit, amount, ref=rec.name, analytic_id=rec.analytic_account_id)
            rec.state = 'closed'

    def action_generate_units(self, units_count=1):
        self.ensure_one()
        if units_count < 1:
            raise UserError(_('Units count must be at least 1.'))
        unit_cost = self.actual_cost / units_count if units_count else 0.0
        for i in range(units_count):
            self.env['real.estate.unit'].create({
                'name': f'{self.name}-U{i + 1}',
                'project_id': self.id,
                'cost': unit_cost,
            })
