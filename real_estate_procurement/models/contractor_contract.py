from odoo import fields, models


class ContractorContract(models.Model):
    _name = 'real.estate.contractor.contract'
    _description = 'Contractor Contract'
    _inherit = ['mail.thread', 'real.estate.accounting.mixin']

    name = fields.Char(required=True)
    project_id = fields.Many2one('real.estate.project', required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    contract_value = fields.Monetary(required=True)
    retention_percentage = fields.Float(default=5.0)
    progress_amount = fields.Monetary(help='Current certified progress amount to bill.')
    retention_amount = fields.Monetary(compute='_compute_retention')
    payable_amount = fields.Monetary(compute='_compute_retention')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    def _compute_retention(self):
        for rec in self:
            rec.retention_amount = rec.progress_amount * rec.retention_percentage / 100
            rec.payable_amount = rec.progress_amount - rec.retention_amount

    def action_post_progress(self):
        for rec in self:
            wip = rec._get_required_account('real_estate_core.wip_account_id')
            payable = rec.partner_id.property_account_payable_id
            retention = rec._get_required_account('real_estate_core.retention_payable_account_id')
            rec._post_simple_entry(wip, payable, rec.payable_amount, rec.partner_id, f'{rec.name} Progress', rec.project_id.analytic_account_id)
            if rec.retention_amount:
                rec._post_simple_entry(wip, retention, rec.retention_amount, rec.partner_id, f'{rec.name} Retention', rec.project_id.analytic_account_id)
