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
import logging
from odoo import fields, models, api, _
# Set up logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'
    phone_search = fields.Char("Phone_search", compute='prepare_phone4search',store="True")
    mobile_search = fields.Char("mobile_search")
    is_writer = fields.Boolean("Is a Writer", default=False)
    is_publisher = fields.Boolean("Is a Publisher", default=False)
    author_of = fields.Many2many(comodel_name="product.template",relation= 'author_book_rel',column1= "author_ids",column2= 'author_of',string="Author Of")
    publisher_of = fields.Many2many(comodel_name="product.template",relation= 'publisher_book_rel',column1= 'publisher_ids', column2='publisher_of',
                                    string="Publisher Of")

    total_balance = fields.Monetary(
        string="Total Balance",
        compute="_compute_total_balance",
        currency_field="currency_id",
    )

    # @api.depends('move_ids.amount_residual')  # Use move_ids instead of account_move_ids
    def _compute_total_balance(self):
        for partner in self:
            # Fetch Payable and Receivable amounts
            partner_balance = partner.debit - partner.credit
            partner.total_balance = partner_balance

    # @api.model
    # def _rec_names_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     domain = ['|', ('phone_search', operator, name), ('mobile_search', operator, name)]
    #     return self.search(domain + args, limit=limit).name_get()

    # @api.model
    # def add_phone_to_search(self):
    #     searchables=self._rec_names_search
    #     if not 'phone' in searchables:
    #         self._rec_names_search.append('phone')
    #         print ("phone is added to searchable")
    @property
    def _rec_names_search(self):
        return super()._rec_names_search + ["phone_search", "mobile_search", "phone", "mobile"]
    # @api.model
    # def init(self):
    #     super(Partner, self).init()
    #     _logger.info("Initializing Partner model and adding fields to _rec_names_search")
    #
    #     # Dynamically add fields to _rec_names_search
    #     if "phone_search" not in self._rec_names_search:
    #         self._rec_names_search.append("phone_search")
    #         _logger.info("Added 'phone_search' to _rec_names_search")
    #     if "mobile_search" not in self._rec_names_search:
    #         self._rec_names_search.append("mobile_search")
    #         _logger.info("Added 'mobile_search' to _rec_names_search")
    #     if "phone" not in self._rec_names_search:
    #         self._rec_names_search.append("phone")
    #         _logger.info("Added 'phone' to _rec_names_search")
    #     if "mobile" not in self._rec_names_search:
    #         self._rec_names_search.append("mobile")
    #         _logger.info("Added 'mobile' to _rec_names_search")
    @api.depends('phone', 'mobile')
    def prepare_phone4search(self):
        for rec in self:
            if rec.phone:
                rec.phone_search = rec.phone.replace(" ", "").replace('-', "")
            if rec.mobile:
                rec.mobile_search = rec.mobile.replace(" ", "").replace('-', "")


    @api.onchange("is_writer")
    def create_related_ecommerce_category_writer(self):
        # todo create a ecommerce category for the writer
        if self.is_writer:
            ecom_categ = self.env['product.public.category'].search([('related_writer_id', '=', self._origin.id)])
            if len(ecom_categ) == 0:
                parent=self.env['ir.model.data']._xmlid_to_res_id('book_shop.product_public_category_author', raise_if_not_found=False)
                ecom_categ.create({'name': self.name,'parent_id':parent, 'related_writer_id': self._origin.id})

    @api.onchange("is_publisher")
    def create_related_ecommerce_category_publisher(self):
        if self.is_publisher:
            ecom_categ = self.env['product.public.category'].search([('related_publisher_id', '=', self._origin.id)])
            if len(ecom_categ) == 0:
                parent = self.env['ir.model.data']._xmlid_to_res_id('book_shop.product_public_category_publication',
                                                                    raise_if_not_found=False)
                ecom_categ.create({'name': self.name,'parent_id':parent, 'related_publisher_id': self._origin.id})
    def get_author_ecom_category(self):
        ecom_categ = self.env['product.public.category'].search([('related_writer_id', '=', self._origin.id)])
        return ecom_categ

    def get_publisher_ecom_category(self):
        ecom_categ = self.env['product.public.category'].search([('related_publisher_id', '=', self._origin.id)])
        return ecom_categ

