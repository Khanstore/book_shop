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

class AccountMove(models.Model):
    _inherit='account.move'

    shipping_address=fields.Char("Shipping Address")
    partner_balance=fields.Monetary("Partner Balance",related="partner_id.commercial_partner_id.total_balance")
    condition_txt=fields.Char("condition Text" ,compute='condition_payment_text')

    @api.onchange('partner_shipping_id')
    def update_shipping_address(self):
        shipping=self.partner_shipping_id
        address=shipping.name
        if shipping.parent_id:
            adress=address + chr(10) +shipping.parent_id.name
        if shipping.street:
            address=address+ chr(10) +shipping.street +", "
        if shipping.street2:
            address=address+ shipping.street2 +", "
        if shipping.city:
            address = address + shipping.city + ", "

        if shipping.state_id:
            address = address + shipping.state_id.name
        if shipping.zip:
            address = address + shipping.zip
        if shipping.phone:
            address = address +chr(10)+ shipping.phone
        if shipping.mobile:
            address = address +chr(10)+ shipping.mobile

        self.shipping_address=address

    def condition_payment_text(self):
        self.condition_txt= "its condition text"

