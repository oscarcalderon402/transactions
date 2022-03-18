# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api


class AccountTransactions(models.Model):
    _name = 'account.transactions'
    _auto = False
    _order = 'date'
    _description = 'Transactions'

    name = fields.Char(string='Label', readonly=True)
    date = fields.Date(string='Date Line', readonly=True)
    ref = fields.Char(string='Ref', readonly=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True)
    type = fields.Selection(selection=[
        ('entry', 'Journal Entry'),
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt'),
    ], string='Type Journal', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    journal_type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
    ], string='Transaction Type', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True, string='Partner')
    account_id = fields.Many2one('account.account', string='Account')
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    cash_advances_id = fields.Char(string='Cash_advances_id', readonly=True)
    payment_ualett_id = fields.Char(string='payment_id', readonly=True)
    x_ualett_principal = fields.Integer(string='Capital', readonly=True)
    x_ualett_fee = fields.Integer(string='Fee', readonly=True)
    capital = fields.Integer(string='P_Capital', readonly=True)
    fee = fields.Integer(string='P_Fee', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency')
    debit = fields.Monetary(string='Debit', default=0.0, currency_field='currency_id')
    credit = fields.Monetary(string='Credit', default=0.0, currency_field='currency_id')
    # balance = fields.Monetary(string='Balance', currency_field='currency_id', compute='_compute_balance')

    # @api.depends('debit', 'credit')
    # def _compute_balance(self):
    #     for line in self:
    #         line.balance = line.debit - line.credit

    # def init(self):
    #     tools.drop_view_if_exists(self.env.cr, self._table)
    #     self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
    #     SELECT
    #         row_number() OVER () AS id,
    #         ac.state,
    #         ac.type as type,
    #         aml.company_id,
    #         aml.currency_id,
    #         aml.date,
    #         aml.journal_id,
    #         aml.partner_id,
    #         aml.debit,
    #         aml.credit,
    #         aml.balance,
    #         aml.move_id,
    #         aml.name,
    #         aml.ref,
    #         aml.account_id,
    #         aj.type as journal_type
    #     FROM account_move ac
    #     LEFT JOIN account_move_line aml ON ac.id = aml.move_id
    #     LEFT JOIN account_journal aj ON aml.journal_id = aj.id
    #     WHERE ac.state IN ('posted') AND
    #     ac.type IN ('entry', 'out_invoice') AND
    #     aml.journal_id IN ('1', '8', '21', '18', '19', '7', '38') AND NOT
    #     aml.account_id IN (6, 51)
    #     )''' % (self._table,))

    _depends = {
        'account.move': [
            'state', 'type', 'cash_advances_id',
        ],
        'account.move.line': [
            'name', 'debit', 'credit', 'partner_id', 'name', 'company_id', 'currency_id', 'date', 'journal_id', 'move_id', 'account_id', 'ref', 'payment_id', 'x_ualett_fee', 'x_ualett_principal'
        ],
        'account.journal': ['type'],
        'account.payment': ['payment_ualett_id', 'capital', 'fee'],
    }

    @api.model
    def _select(self):
        return '''
            SELECT
            aml.id,
            ac.state, 
            ac.type, 
            ac.cash_advances_id,
            aml.company_id, 
            aml.currency_id, 
            aml.date, 
            aml.journal_id, 
            aml.partner_id, 
            aml.debit, 
            aml.credit,
            aml.move_id, 
            aml.name,
            aml.ref,
            aml.account_id,
            aml.payment_id,
            aml.x_ualett_fee,
            aml.x_ualett_principal,
            aj.type as journal_type,
            ap.capital,
            ap.fee, 
            ap.payment_ualett_id
           '''

    @api.model
    def _from(self):
        return '''
               FROM account_move ac 
               LEFT JOIN account_move_line aml ON ac.id = aml.move_id 
               LEFT JOIN account_journal aj ON aml.journal_id = aj.id 
               LEFT JOIN account_payment ap ON aml.payment_id = ap.id
           '''

    @api.model
    def _where(self):
        return '''
               WHERE ac.state IN ('posted') AND 
               ac.type IN ('entry', 'out_invoice') AND 
               aml.journal_id IN ('1', '8', '21', '18', '19', '7', '38') AND NOT 
               aml.account_id IN (6, 51) AND 
               aml.name NOT LIKE '%Vendor%' AND 
               aml.name NOT LIKE '%SUPP%'
           '''

    # @api.model
    # def _when(self):
    #     return '''
    #           CASE WHEN aml.journal_id = 1 THEN 'Cash Advances'
    #           ELSE 'Payments'
	# 	        END AS name
    #        '''

    @api.model
    def _group_by(self):
        return '''
            GROUP BY
                aml.id,
                aml.name,
                ac.type,
                ac.date,
                ac.state,
                aml.company_id,
                aml.journal_id,
                aml.partner_id,
                aml.move_id,
                aml.account_id,
                aml.x_ualett_fee,
                ac.cash_advances_id,
                aj.type,
                ap.capital,
                ap.fee, 
                ap.payment_ualett_id
        '''

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
                CREATE OR REPLACE VIEW %s AS (
                    %s %s %s %s
                )
            ''' % (
            self._table, self._select(), self._from(), self._where(), self._group_by()
        ))
