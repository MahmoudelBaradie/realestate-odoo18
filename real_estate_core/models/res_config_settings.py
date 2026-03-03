from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    re_land_asset_account_id = fields.Many2one(
        'account.account',
        config_parameter='real_estate_core.land_asset_account_id',
        string='Land Asset Account',
    )

    re_cash_bank_account_id = fields.Many2one(
        'account.account',
        config_parameter='real_estate_core.cash_bank_account_id',
        string='Cash/Bank Clearing Account',
    )
    re_wip_account_id = fields.Many2one(
        'account.account',
        config_parameter='real_estate_core.wip_account_id',
        string='WIP Account',
    )
    re_inventory_account_id = fields.Many2one(
        'account.account',
        config_parameter='real_estate_core.inventory_account_id',
        string='Inventory Units Account',
    )
    re_investment_property_account_id = fields.Many2one(
        'account.account',
        config_parameter='real_estate_core.investment_property_account_id',
        string='Investment Property Account',
    )
    re_cost_of_sales_account_id = fields.Many2one(
        'account.account',
        config_parameter='real_estate_core.cost_of_sales_account_id',
        string='Cost of Sales Account',
    )
    re_sales_revenue_account_id = fields.Many2one(
        'account.account',
        config_parameter='real_estate_core.sales_revenue_account_id',
        string='Sales Revenue Account',
    )
    re_rental_revenue_account_id = fields.Many2one(
        'account.account',
        config_parameter='real_estate_core.rental_revenue_account_id',
        string='Rental Revenue Account',
    )
    re_security_deposit_account_id = fields.Many2one(
        'account.account',
        config_parameter='real_estate_core.security_deposit_account_id',
        string='Security Deposit Liability Account',
    )
    re_retention_payable_account_id = fields.Many2one(
        'account.account',
        config_parameter='real_estate_core.retention_payable_account_id',
        string='Retention Payable Account',
    )
