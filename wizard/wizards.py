# -*- coding: utf-8 -*-
###################################################################################
#
#    Eagle ERP  Ltd.
#    Copyright (C) 2021 Eagle ERP Ltd(<http://www.eagle_it_solutions.com>).
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

class DailyStatementWizard(models.TransientModel):
    _name ='book.shop.daily.statement'
    _description ='Create a statement which reflects every action or change in certain date'

    name =fields.Char("Daily Administrative Statement")
    date_start =fields.Date("Start",default=lambda self: datetime.today().date() - timedelta(days=1))
    date_end =fields.Date("Up to",default=fields.Date.today)
    mode=fields.Selection(string='Report mode',
        selection=[('short', 'Short'), ('long', 'Long')],
        default="short")
    sales_new =fields.Many2many(comodel_name='sale.order' ,string='sales' ,compute='get_sales_new')
    purchase_new =fields.Many2many(comodel_name='purchase.order' ,string='Purchase' ,compute='get_purchase_new')
    payment_new =fields.Many2many(comodel_name='account.payment' ,string='Payments' ,compute='get_payment_new')
    # sales_edit =fields.Many2many(comodel_name='sale.order' ,string='sales' ,compute='get_sales_edit')
    journals =fields.Many2many(comodel_name='account.journal' ,string='Bank Balances' ,compute='get_journals')
    def get_sales_new(self):
        orders =self.env['sale.order'].search([('create_date' ,'>=' ,datetime.combine(self.date_start, datetime.min.time())),
                                               ('create_date' ,'<=' ,datetime.combine(self.date_start, datetime.max.time()))])

        self.sales_new=[(6, 0, orders.ids)]

    def get_purchase_new(self):
        orders =self.env['purchase.order'].search([('create_date' ,'>=' ,datetime.combine(self.date_start, datetime.min.time())),
                                               ('create_date' ,'<=' ,datetime.combine(self.date_start, datetime.max.time()))])

        self.purchase_new=[(6, 0, orders.ids)]

    def get_balance(self,journals,date_end=None):
        domain=[('journal_id', '=', journals),('account_id.account_type','=','asset_cash')]
        if date_end != None:
            domain.append(('date_maturity', '<=', date_end))
        return self.env['account.move.line'].read_group(
            domain,  ['balance:sum'], [])[0]['balance']

    def get_journals(self):
        journals =self.env['account.journal'].search([('type' ,'in' ,['bank', 'cash'])])

        self.journals=[(6, 0, journals.ids)]

    def get_payment_new(self):
        orders =self.env['account.payment'].search([('create_date' ,'>=' ,datetime.combine(self.date_start, datetime.min.time())),
                                               ('create_date' ,'<=' ,datetime.combine(self.date_end, datetime.max.time()))])

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
        self.get_purchase_new()
        self.get_payment_new()
        self.get_journals()
        # self.get_sales_edit()
