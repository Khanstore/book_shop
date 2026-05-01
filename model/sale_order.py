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

from odoo import fields, models, api, _

class SaleOrder(models.Model):
    _inherit='sale.order'

    partner_balance=fields.Monetary("Partner Balance",related="partner_id.commercial_partner_id.total_balance")

    def test(self,data):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': data['invoice_id'],
            'view_mode': 'form',
            'target': 'current',
        }
    def action_complete_invoice_delivery(self):
        self.action_confirm()
        self.picking_ids.button_validate()
        invoice = self._create_invoices()
        invoice.action_post()
        self.test({'invoice_id':invoice.id})
        print ("yes")
        # Open the invoice record (example: returning its form view in Odoo)


    
class saleOrderLine(models.Model):
    _inherit ='sale.order.line'

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True, index='btree_not_null')
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date', readonly=True)
    date_approve = fields.Datetime(related="order_id.date_order", string='Confirmation Date', readonly=True)
    sequence = fields.Integer(string="Sequence", default=1)

    def action_sale_history(self):
        self.ensure_one()

        # Define the action dictionary from scratch
        return {
            'name': f"Sales History: {self.product_id.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line',
            'view_mode': 'list,pivot,graph',
            # Hard domain to ensure we only see relevant, completed sales
            'domain': [
                # ('product_id', '=', self.product_id.id),
                ('state', 'in', ['sale', 'done'])
            ],
            'context': {
                # Order matters: Product will appear LEFT, Partner will appear RIGHT
                'search_default_product_id': self.product_id.id,
                'search_default_order_partner_id': self.order_id.partner_id.id,
                # Optional: Group by date or customer by default
                'search_default_groupby_customer': 1,
            },
            'target': 'new',  # Opens in a pop-up (use 'current' to switch screens)
        }

    # the components instantly recompute!
        for line in self:
                    # Derive the price from the component's actual value.
