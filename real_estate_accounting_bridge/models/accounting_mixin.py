from odoo import _, models
from odoo.exceptions import UserError


class RealEstateAccountingMixin(models.AbstractModel):
    _name = 'real.estate.accounting.mixin'
    _description = 'Real Estate Accounting Helper Mixin'

    def _get_required_account(self, key):
        account_id = int(self.env['ir.config_parameter'].sudo().get_param(key, default=0))
        if not account_id:
            raise UserError(_('Missing configuration for %s') % key)
        return self.env['account.account'].browse(account_id)

    def _post_simple_entry(self, debit_account, credit_account, amount, partner_id=False, ref=False, analytic_id=False):
        if amount <= 0:
            raise UserError(_('Amount must be positive to generate accounting entries.'))
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'ref': ref,
            'line_ids': [
                (0, 0, {
                    'name': ref or '/',
                    'account_id': debit_account.id,
                    'debit': amount,
                    'credit': 0.0,
                    'partner_id': partner_id.id if partner_id else False,
                    'analytic_distribution': {analytic_id.id: 100} if analytic_id else False,
                }),
                (0, 0, {
                    'name': ref or '/',
                    'account_id': credit_account.id,
                    'debit': 0.0,
                    'credit': amount,
                    'partner_id': partner_id.id if partner_id else False,
                    'analytic_distribution': {analytic_id.id: 100} if analytic_id else False,
                }),
            ]
        })
        move.action_post()
        return move
