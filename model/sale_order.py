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
    report_grids = fields.Boolean(string="Print Variant Grids", default=False)

    partner_balance=fields.Monetary("Partner Balance",related="partner_id.commercial_partner_id.total_balance")
    delivery_address=fields.Text(string="Delivery Address", compute="_compute_shipping_address", store=True)


    def test(self,data):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': data['invoice_id'],
            'view_mode': 'form',
            'target': 'current',
        }

    @api.depends('partner_shipping_id')
    def _compute_shipping_address(self):
        for rec in self:
            partner = rec.partner_shipping_id
            if partner:
                address = partner.contact_address or ''
                phone = partner.phone or ''
                mobile = partner.mobile or ''

                rec.delivery_address = f"{address}\nPhone: {phone}\nMobile: {mobile}"
            else:
                rec.delivery_address = ''

    def action_complete_invoice_delivery(self):
        self.action_confirm()
        self.picking_ids.button_validate()
        invoice = self._create_invoices()
        invoice.action_post()
        self.test({'invoice_id':invoice.id})
        print ("yes")
        # Open the invoice record (example: returning its form view in Odoo)

    # @api.onchange('order_line', 'order_line.price_unit')
    # def _onchange_combo_line_pricing(self):
    #     """
    #     Triggered in real-time whenever an order line
    #     or a unit price within those lines is modified.
    #     """
    #     for line in self.order_line:
    #         # Check if this line is a component linked to a parent
    #         if line.linked_line_id:
    #             parent_line = line.linked_line_id
    #
    #             if parent_line.price_unit > 0.0:
    #                 # Parent has a price? Component becomes 0.
    #                 if line.price_unit != 0.0:
    #                     line.price_unit = 0.0
    #             else:
    #                 # Parent price is 0? Component pulls its real list price.
    #                 # We only set it if it's currently 0 to avoid overwriting
    #                 # manual edits you might have made.
    #                 if line.price_unit == 0.0:
    #                     line.price_unit = line.product_id.list_price
    #         # else :
    #         #     line.price_unit = self.pricelist_id._get_product_price(line.product_id,
    #         #                                                          line.product_uom_qty)


    
class saleOrderLine(models.Model):
    _inherit ='sale.order.line'

    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True,recursive=True)

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

    # We add a dependency so if you manually change the parent's price to 0 in the UI,
    # the components instantly recompute!
    @api.depends('linked_line_id.price_unit')
    def _compute_price_unit(self):
        # 1. Let Odoo run its default calculations first
        super()._compute_price_unit()

        # 2. Apply our custom dynamic pricing logic
        for line in self:
            # Check if this line is a component (has a parent combo line)
            # Note: 'linked_line_id' is the standard Odoo relation field.
            # If you are using a specific third-party combo module, this might be 'combo_parent_id'
            if line.linked_line_id:
                parent_line = line.linked_line_id

                if parent_line.order_id.pricelist_id._get_product_price(parent_line.product_id, parent_line.product_uom_qty) > 0.0:
                    # Scenario A: You set a price on the Combo Parent (e.g., 380 ৳).
                    # Hide the component prices to avoid double charging.
                    line.price_unit = 0.0
                else:
                    # Scenario B: You left the Combo Parent at 0.00 ৳.
                    # Derive the price from the component's actual value.

                    # This pulls the standard product price.
                    # (Use line._get_display_price() instead if you want to strictly enforce complex pricelists)
                    pricelist = line.order_id.pricelist_id  # or wherever your pricelist comes from
                    product = line.product_id
                    qty = line.product_uom_qty or 1.0
                    # partner = line.order_id.partner_id

                    price = pricelist._get_product_price(product, qty)

                    line.price_unit = price