# -*- coding: utf-8 -*-
###################################################################################
#
#    Eagle ERP  Ltd.
#    Copyright (C) 2024 Eagle ERP Ltd(<http://www.eagle_it_solutions.com>).
#    Author: SM Ashraf
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import urllib
import base64
from datetime import datetime, timedelta
from odoo import fields, models, api, _
from collections import defaultdict


def group_by_journal(vals_list):
    res = defaultdict(list)
    for vals in vals_list:
        res[vals['journal_id']].append(vals)
    return res

class DailyStatementWizard(models.TransientModel):
    _name ='book.shop.daily.statement'
    _description ='Create a statement which reflects every action or change in certain date'

    name =fields.Char("Daily Administrative Statement")
    date_start =fields.Date("Start",default=lambda self: datetime.today().date() - timedelta(days=1))
    date_end =fields.Date("Up to",default=fields.Date.today)
    mode=fields.Selection(string='Report mode',
        selection=[('short', 'Short'), ('long', 'Long')],
        default="short")
    sales_new =fields.Many2many(comodel_name='sale.order' ,string='Sales' ,compute='get_sales_new')
    quote_new =fields.Many2many(comodel_name='sale.order' ,string='Quotation' ,compute='get_quote_new')
    purchase_new =fields.Many2many(comodel_name='purchase.order' ,string='Purchase' ,compute='get_purchase_new')
    purchase_new =fields.Many2many(comodel_name='purchase.order' ,string='Purchase' ,compute='get_purchase_new')
    payment_new =fields.Many2many(comodel_name='account.payment' ,string='Payments' ,compute='get_payment_new')
    # sales_edit =fields.Many2many(comodel_name='sale.order' ,string='sales' ,compute='get_sales_edit')
    journals =fields.Many2many(comodel_name='account.journal' ,string='Bank Balances' ,compute='get_journals')

    @api.onchange('date_start', 'date_end')
    def get_sales_new(self):
        orders =self.env['sale.order'].search([('date_order' ,'>=' ,datetime.combine(self.date_start, datetime.min.time())),
                                               ('date_order' ,'<=' ,datetime.combine(self.date_end, datetime.max.time())),
                                               ('state', '=', 'sale')])

        self.sales_new=[(6, 0, orders.ids)]

    @api.onchange('date_start', 'date_end')
    def get_quote_new(self):
        quotes = self.env['sale.order'].search([
            ('date_order', '>=', datetime.combine(self.date_start, datetime.min.time())),
            ('date_order', '<=', datetime.combine(self.date_end, datetime.max.time())),
            ('state', 'in', ['draft', 'sent'])
        ], order='id desc')

        self.quote_new=[(6, 0, quotes.ids)]

    @api.onchange('date_start', 'date_end')
    def get_purchase_new(self):
        purchase =self.env['purchase.order'].search([('date_approve' ,'>=' ,datetime.combine(self.date_start, datetime.min.time())),
                                               ('date_approve' ,'<=' ,datetime.combine(self.date_end, datetime.max.time()))])

        self.purchase_new=[(6, 0, purchase.ids)]


    @api.onchange('date_start', 'date_end')
    def get_purchase_quote(self):
        p_quote =self.env['purchase.order'].search([('date_order' ,'>=' ,datetime.combine(self.date_start, datetime.min.time())),
                                               ('date_order' ,'<=' ,datetime.combine(self.date_end, datetime.max.time())),
                                                    ('state', 'in', ['draft', 'sent'])])

        self.purchase_new=[(6, 0, p_quote.ids)]

    def get_previous_date(self, date):
        return date - timedelta(days=1)



    def _get_journal_dashboard_bank_running_balance(self, date=None, including=False):
        # In order to not recompute everything from the start, we take the last
        # bank statement and only sum starting from there.
        if not date:
            date = fields.Date.context_today(self)

        if including:
            date=datetime.today() + timedelta(days=1)
        journals = self.env['account.journal'].search([('type', 'in', ('bank', 'cash', 'credit'))])


        params = {
            'on_date': date ,
            'journals': journals.ids,
            'companies': self.env.companies.ids,
        }

        self._cr.execute("""
            SELECT journal.id AS journal_id,
                   statement.id AS statement_id,
                   COALESCE(statement.balance_end_real, 0) AS balance_end_real,
                   without_statement.amount AS unlinked_amount,
                   without_statement.count AS unlinked_count
              FROM account_journal journal
         LEFT JOIN LATERAL (  -- select latest statement based on the date
                           SELECT id,
                                  first_line_index,
                                  balance_end_real
                             FROM account_bank_statement
                            WHERE journal_id = journal.id
                              AND company_id = 1
                         ORDER BY date DESC, id DESC
                            LIMIT 1
                   ) statement ON TRUE
         LEFT JOIN LATERAL (  -- sum all the lines not linked to a statement with a higher index than the last line of the statement
                           SELECT COALESCE(SUM(stl.amount), 0.0) AS amount,
                                  COUNT(*)
                             FROM account_bank_statement_line stl
                             JOIN account_move move ON move.id = stl.move_id
                            WHERE stl.statement_id IS NULL
                              AND move.date < %(on_date)s
                              AND move.state != 'cancel'
                              AND stl.journal_id = journal.id
                              AND stl.company_id = 1
                              AND stl.internal_index >= COALESCE(statement.first_line_index, '')
                            LIMIT 1
                   ) without_statement ON TRUE
             WHERE journal.id = ANY(%(journals)s)
			 
        """, params)
        query_res = {res['journal_id']: res for res in self.env.cr.dictfetchall()}
        result = {}
        for journal in self.journals:
            journal_vals = query_res[journal.id]
            result[journal.id] = (
                bool(journal_vals['statement_id'] or journal_vals['unlinked_count']),
                journal_vals['balance_end_real'] + journal_vals['unlinked_amount'],
            )
        return result

    def get_balance(self,journals,date_end=None):
        domain=[('journal_id', '=', journals),('account_id.account_type','=','asset_cash')]
        if date_end != None:
            domain.append(('date', '<=', date_end))
        return self.env['account.move.line'].read_group(
            domain,  ['balance:sum'], [])[0]['balance']

    def get_balance_with_suspense(self, journals, date_end=None):

        journal=self.env['account.journal'].search([('id', '=', journals)])

        suspense_account= journal.suspense_account_id
        base_domain = [('journal_id', '=', journal.id)]
        if date_end:
            base_domain.append(('date', '<=', date_end))

        confirmed_domain = base_domain + [('account_id.account_type', '=', 'asset_cash'),
                                          ('account_id', '!=', suspense_account.id),
                                          ('parent_state', '=', 'posted')]
        suspense_domain = base_domain + [('account_id', '=', suspense_account.id)]
        cancel_domain = base_domain + [('parent_state', '!=', 'posted')]

        confirmed = self.env['account.move.line'].read_group(confirmed_domain, ['balance:sum'], [])
        suspense = self.env['account.move.line'].read_group(suspense_domain, ['balance:sum'], [])
        cancel = journal._get_journal_bank_account_balance

        confirmed_balance = confirmed[0]['balance'] if confirmed else 0.0
        suspense_balance = suspense[0]['balance'] if suspense else 0.0
        cncel_balance = journal._get_journal_bank_account_balance()

        return {
            'confirmed_balance': confirmed_balance,
            'suspense_balance': suspense_balance,
            'cancel_balance': cncel_balance,
            'total_balance': confirmed_balance + suspense_balance
        }


    def get_journals(self):
        journals =self.env['account.journal'].search([('type', 'in', ('bank', 'cash', 'credit'))])

        self.journals=[(6, 0, journals.ids)]

    def _get_suspend_bank_payments(self, date=None, including=False):
        journals = self.env['account.journal'].search([('type', 'in', ('bank', 'cash', 'credit'))])
        query = """
            SELECT move.journal_id AS journal_id,
                   move.company_id AS company_id,
                   move.currency_id AS currency,
                   SUM(CASE
                       WHEN payment.payment_type = 'outbound' THEN -payment.amount
                       ELSE payment.amount
                   END) AS amount_total,
                   SUM(amount_company_currency_signed) AS amount_total_company
              FROM account_payment payment
              JOIN account_move move ON move.origin_payment_id = payment.id
              JOIN account_journal journal ON move.journal_id = journal.id
             WHERE payment.is_matched IS False
               AND move.state = 'posted'
               and move.date < %(on_date)s
               AND payment.journal_id = ANY(%s)
               AND payment.company_id = ANY(%s)
               AND payment.outstanding_account_id = journal.suspense_account_id
        """

        params = [journals.ids, self.env.companies.ids]

        if date:
            if including:
                query += " AND move.date <= %s"
            else:
                query += " AND move.date < %s"
            params.append(date)

        query += " GROUP BY move.company_id, move.journal_id, move.currency_id"

        self.env.cr.execute(query, params)
        query_result = group_by_journal(self.env.cr.dictfetchall())

        result = {}
        for journal in journals:
            currency = (journal.currency_id or journal.company_id.sudo().currency_id).with_env(self.env)
            result[journal.id] = self._count_results_and_sum_amounts(query_result.get(journal.id, []), currency)

        return result

    def _get_direct_bank_payments(self, date=None, including=False):
        journals = self.env['account.journal'].search([('type', 'in', ('bank', 'cash', 'credit'))])
        if not date:
            date = fields.Date.context_today(self)

        if including:
            date=datetime.today() + timedelta(days=1)
        params = {
            'on_date': date,
            'journals': journals.ids,
            'companies': self.env.companies.ids,
        }

        query = """
            
SELECT move.journal_id AS journal_id,
                   move.company_id AS company_id,
                   move.currency_id AS currency,
                   SUM(CASE
                       WHEN payment.payment_type = 'outbound' THEN -payment.amount
                       ELSE payment.amount
                   END) AS amount_total,
                   SUM(amount_company_currency_signed) AS amount_total_company
              FROM account_payment payment
              JOIN account_move move ON move.origin_payment_id = payment.id
              JOIN account_journal journal ON move.journal_id = journal.id
             WHERE payment.is_matched IS TRUE
               AND move.state = 'posted'
               AND payment.journal_id = ANY(%(journals)s)
               AND payment.company_id = ANY(%(companies)s)
               and move.date < %(on_date)s
               AND payment.outstanding_account_id = journal.default_account_id
          GROUP BY move.company_id, move.journal_id, move.currency_id
        """



        self.env.cr.execute(query, params)
        query_result = group_by_journal(self.env.cr.dictfetchall())

        result = {}
        for journal in journals:
            currency = (journal.currency_id or journal.company_id.sudo().currency_id).with_env(self.env)
            result[journal.id] = self._count_results_and_sum_amounts(query_result.get(journal.id, []), currency)

        return result

    def _count_results_and_sum_amounts(self, results_dict, target_currency):
        """ Loops on a query result to count the total number of invoices and sum
        their amount_total field (expressed in the given target currency).
        amount_total must be signed!
        """
        total_amount = 0
        count = 0
        for result in results_dict:
            document_currency = self.env['res.currency'].browse(result.get('currency'))
            company = self.env['res.company'].browse(result.get('company_id')) or self.env.company
            date = result.get('invoice_date') or fields.Date.context_today(self)

            count += result.get('count', 1)
            if company.currency_id == target_currency:
                total_amount += result.get('amount_total_company') or 0
            else:
                total_amount += document_currency._convert(result.get('amount_total'), target_currency, company, date)
        return (count, target_currency.round(total_amount))

    @api.onchange('date_start', 'date_end')
    def get_payment_new(self):
        orders =self.env['account.payment'].search([('date' ,'>=' ,datetime.combine(self.date_start, datetime.min.time())),
                                               ('date' ,'<=' ,datetime.combine(self.date_end, datetime.max.time())),
                                                    ('move_id','!=',False)])

        self.payment_new=[(6, 0, orders.ids)]

    # def get_sales_edit(self):
    #     orders = self.env['sale.order'].search([
    #         ('write_date', '>=', datetime.combine(self.date_start, datetime.min.time())),
    #         ('write_date', '<=', datetime.combine(self.date_start, datetime.max.time())),
    #         '!AND',  # Exclude the following 'AND' conditions
    #         ('create_date', '>=', datetime.combine(self.date_start, datetime.min.time())),
    #         ('create_date', '<=', datetime.combine(self.date_start, datetime.min.time()))
    #     ])
    #     self.sales_edit = [(6, 0, orders.ids)]

    def update_fields(self):
        self.get_sales_new()
        self.get_quote_new()
        self.get_purchase_new()
        self.get_payment_new()
        self.get_journals()
        self.get_sales_edit()
