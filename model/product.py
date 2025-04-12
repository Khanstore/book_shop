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
from odoo.osv import expression

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    printed_name=fields.Char('Name')
    is_book = fields.Boolean("Is A Book")
    isbn = fields.Char(string="ISBN")
    author_ids = fields.Many2many(comodel_name="res.partner", relation='author_book_rel',column1='author_of',column2="author_ids", string="Author")
    publisher_ids = fields.Many2many(comodel_name="res.partner",relation='publisher_book_rel',column1='publisher_of',column2='publisher_ids',string="Publisher")
    # "res.partner",'publisher_book_rel','published_books','publisher_ids',string="Publisher"
    publication_date = fields.Char(string="Publication Date")
    last_edition=fields.Char(string="Last Edition")
    genre = fields.Many2one('product.genre', string="Genre")
    binding_type=fields.Many2one("book.binding.type")
    total_page = fields.Integer("Page")
    paper_gsm = fields.Integer("GSM")
    paper_color = fields.Many2one("book.paper.color", string="Colour")
    paper_quality = fields.Many2one("paper.quality", string="Paper Quality")
    length=fields.Float("lenght")
    height=fields.Float("Height")
    width=fields.Float("Width")
    
    # set variant fields with same value while only one variant
    def write(self, vals):
        update_product = True
        if "no_update" in vals:
            del vals["no_update"]
            update_product= False 
        res = super(ProductTemplate, self).write(vals)
        if self.product_variant_count == 1 and update_product :
            if 'list_price' in vals:
                self.product_variant_id.write({'list_price': vals['list_price'],'no_update':True})
            if 'standard_price' in vals:
                self.product_variant_id.write({'standard_price': vals['standard_price'],'no_update':True})
        return res

    @api.onchange('categ_id')
    def define_book_product(self):
        for rec in self:
            category = rec.categ_id
            rec.is_book = False
            while category:
                # fixme correction of external id
                if category.get_external_id()[category.id] == 'book_shop.product_category_book':
                    rec.is_book = True
                    return
                else:
                    if category.parent_id.id:
                        category = category.parent_id
                    else:
                        category = False

    @api.onchange('author_ids')
    def writer_ids_onchange(self):
        ecom_categ = self.public_categ_ids
        for rec in ecom_categ:
            if rec.related_writer_id:
                self.public_categ_ids = [(3, rec._origin.id)]
        for line in self.author_ids:
            new_ecom_categ = self.env['product.public.category'].search(
                [('related_writer_id', '=', line._origin.id)])
            self.public_categ_ids = [(4, new_ecom_categ.id)]

    @api.onchange('publisher_ids')
    def publisher_ids_onchange(self):
        ecom_categ = self.public_categ_ids
        for rec in ecom_categ:
            if rec.related_publisher_id:
                self.public_categ_ids = [(3, rec._origin.id)]
        for line in self.publisher_ids:
            new_ecom_categ = self.env['product.public.category'].search(
                [('related_publisher_id', '=', line._origin.id)])
            self.public_categ_ids = [(4, new_ecom_categ.id)]

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     domain = [('name', operator, name)]  # Default search in current language
    #
    #     # Fetch translations dynamically using Odoo’s `with_context` method
    #     translated_product_ids = set()
    #     active_langs = self.env['res.lang'].search([('active', '=', True)])
    #
    #     for lang in active_langs:
    #         translated_products = self.with_context(lang=lang.code).search([('name', operator, name)], limit=limit)
    #         translated_product_ids.update(translated_products.ids)
    #
    #     if translated_product_ids:
    #         domain = ['|'] + domain + [('id', 'in', list(translated_product_ids))]
    #
    #     return self.search(domain + args, limit=limit).name_get()
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        search_domain = [('name', operator, name)]  # Default search in the current language

        # Get all active languages
        active_langs = self.env['res.lang'].search([('active', '=', True)])
        product_ids = set()

        # Search product names in all active languages
        for lang in active_langs:
            translated_products = self.with_context(lang=lang.code).search([('name', operator, name)], limit=limit)
            product_ids.update(translated_products.ids)

        # Add translated product IDs to the search domain
        if product_ids:
            search_domain = ['|'] + search_domain + [('id', 'in', list(product_ids))]

        # Search for products
        products = self.search(search_domain + args, limit=limit)

        # Return product names manually
        return [(prod.id, prod.name) for prod in products]  # Odoo 18 workaround


class ProductProduct(models.Model):
    _inherit= 'product.product'

    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price',
        tracking=True,
        help="Price at which the product is sold to customers.",
    )
    publication_date = fields.Char(string="Publication Date")
    last_edition = fields.Char(string="Last Edition")
    genre = fields.Many2one('product.genre', string="Genre")
    binding_type = fields.Many2one("book.binding.type")
    total_page = fields.Integer("Page")
    length = fields.Float("lenght")
    height = fields.Float("Height")
    width = fields.Float("Width")

    # set template fields with same value while only one variant
    def write(self, vals):
        update_template = True
        if "no_update" in vals:
            del vals["no_update"]
            update_template = False
        res = super(ProductProduct, self).write(vals)
        tmpl=self.product_tmpl_id
        if tmpl.product_variant_count == 1 and update_template:
            vals['no_update'] = True
            if 'list_price' in vals:
                tmpl.write({'list_price': vals['list_price'],'no_update':True})
            if 'standard_price' in vals:
                tmpl.write({'standard_price': vals['standard_price'],'no_update':True})
        return res
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # multi langual search is working 
        user_lang = self.env.context.get('lang', 'en_US')
        domain = args or []
        positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
        is_positive = operator not in expression.NEGATIVE_TERM_OPERATORS
        matched_ids = set()

        # Search in all active languages
        active_langs = self.env['res.lang'].search([('active', '=', True)]).mapped('code')

        for lang_code in active_langs:
            env_lang = self.with_context(lang=lang_code)

            # Try exact code/barcode matches first (fast lookup)
            products = env_lang.search(expression.AND([domain, [('default_code', '=', name)]]), limit=limit)
            products |= env_lang.search(expression.AND([domain, [('barcode', '=', name)]]), limit=limit)

            if not products and is_positive:
                products = env_lang.search(expression.AND([domain, [('default_code', operator, name)]]),
                                           limit=limit)
                limit_rest = limit and limit - len(products)
                if limit_rest is None or limit_rest > 0:
                    products |= env_lang.search(
                        expression.AND([
                            domain,
                            [('id', 'not in', list(matched_ids)), ('name', operator, name)]
                        ]), limit=limit_rest
                    )
            elif not products and not is_positive:
                products = env_lang.search(
                    expression.AND([
                        domain,
                        [('name', operator, name), '|', ('default_code', operator, name),
                         ('default_code', '=', False)]
                    ]), limit=limit
                )

            matched_ids.update(products.ids)

            # Stop early if limit is reached
            if limit and len(matched_ids) >= limit:
                break

        # Final result in user's language
        final_products = self.browse(list(matched_ids)).with_context(lang=user_lang)
        return [(product.id, product.display_name) for product in final_products.sudo()]


class ProductGenre(models.Model):
    _name = 'product.genre'
    _description = 'Book Genre'
    name = fields.Char(string="Genre", required=True ,translate=True)
    description = fields.Char(string="Description", required=True,translate=True)

class ProductPublicCategory(models.Model):
    _inherit='product.public.category'
    _description='this modules adds product public categories for writer and publishers'
    related_writer_id=fields.Many2one('res.partner',"Writer")
    related_publisher_id=fields.Many2one('res.partner',"Publisher")

# class PaperQuality(models.Model):
#     _name = 'paper.type'
#     _description = 'Type Of Paper'
#     name = fields.Char("Paper Type",compute='get_paper_name')
#     gsm= fields.Integer("GSM")
#     paper_quality=fields.Many2one ("paper.quality","Paper quality")
#     paper_color= fields.Many2one("book.paper.color",string="colour")
#     description = fields.Char("description")
#
#     @api.onchange('gsm','paper_type','color')
#     def get_paper_name(self):
#         for rec in self:
#             paper=""
#             if rec.gsm:
#                 paper=str(rec.gsm) + " gram "
#
#             if rec.paper_color :
#                 paper=paper +rec.paper_color.name +" "
#             if rec.paper_quality :
#                 paper=paper +rec.paper_quality.name +" "
#             if rec.description :
#                 paper=paper +"("+ rec.description+")"
#             rec.name=paper
#

class PaperColor(models.Model):
    _name = 'book.paper.color'
    _description = 'Color Of Paper'
    name = fields.Char("Paper Color")
    description = fields.Char("description")

class PaperType(models.Model):
    _name = 'paper.quality'
    _description = 'Quality Of Paper'
    name = fields.Char("Paper Quality")
    description = fields.Char("description")

class BookBindingType(models.Model):
    _name = 'book.binding.type'
    _description = 'Type Of Available Binding'
    name= fields.Char("Binding Type")
    description=fields.Char("description")
    image=fields.Binary("Image", help='Image for binding Type.')

class ProductPublicCategory(models.Model):
    _inherit='product.public.category'
    _description='this modules adds product public categories for writer and publishers'
    related_writer_id=fields.Many2one('res.partner',"Writer")
    related_publisher_id=fields.Many2one('res.partner',"Publisher")



