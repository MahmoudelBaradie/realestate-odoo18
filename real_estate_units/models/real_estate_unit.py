from odoo import fields, models


class RealEstateUnit(models.Model):
    _name = 'real.estate.unit'
    _description = 'Real Estate Unit'

    name = fields.Char(required=True)
    project_id = fields.Many2one('real.estate.project')
    unit_type = fields.Selection([('apartment', 'Apartment'), ('villa', 'Villa'), ('shop', 'Shop'), ('office', 'Office')])
    area = fields.Float()
    cost = fields.Monetary()
    target_price = fields.Monetary()
    status = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ], default='available')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
