from odoo import fields, models


class InvestmentProperty(models.Model):
    _name = 'real.estate.investment.property'
    _description = 'Investment Property Register'

    name = fields.Char(required=True)
    project_id = fields.Many2one('real.estate.project', required=True)
    unit_ids = fields.Many2many('real.estate.unit')
    capitalization_value = fields.Monetary()
    occupancy_rate = fields.Float(compute='_compute_occupancy')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    def _compute_occupancy(self):
        for rec in self:
            total = len(rec.unit_ids)
            rented = len(rec.unit_ids.filtered(lambda u: u.status == 'rented'))
            rec.occupancy_rate = (rented / total * 100) if total else 0.0
