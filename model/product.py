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

# from pygments.lexer import default

from odoo import fields, models, api, _
from odoo.osv import expression
from odoo.tools.translate import html_translate

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    printed_name=fields.Char('Name')
    is_book = fields.Boolean(
        "Is A Book",
        compute='_compute_is_book',
        store=True,  # store=True so it works in domains/filters too
    )
    isbn = fields.Char(string="ISBN")
    author_ids = fields.Many2many(comodel_name="res.partner", relation='author_book_rel',column1='author_of',column2="author_ids", string="Author")
    publisher_ids = fields.Many2many(comodel_name="res.partner",relation='publisher_book_rel',column1='publisher_of',column2='publisher_ids',string="Publisher")
    # todo add translatro colum
    # "res.partner",'publisher_book_rel','published_books','publisher_ids',string="Publisher"
    publication_date = fields.Char(string="Publication Date")
    last_edition=fields.Char(string="Last Edition")
    genre = fields.Many2one('product.genre', string="Genre")
    binding_type=fields.Many2one("book.binding.type")
    pages = fields.Integer(string="Page")
    paper_gsm = fields.Integer("GSM")
    paper_color = fields.Many2one("book.paper.color", string="Colour")
    paper_quality = fields.Many2one("paper.quality", string="Paper Quality")
    length=fields.Float("lenght")
    height=fields.Float("Height")
    width=fields.Float("Width")

    def create(self,vals):
        res=super().create(vals)
        product=self.env['product.product'].search([('product_tmpl_id','=',res.id)])
        dict={}
        for key in vals:
            if isinstance(key, str) and key in product._fields:
                dict[key]=vals[key]
        product.write(dict)
        return res


    def write(self, vals):
        res = super().write(vals)
        for template in self:
            if len(template.product_variant_ids) == 1:
                if 'list_price' in vals:
                    template.product_variant_id.list_price = vals['list_price']
                variant = template.product_variant_ids[0]
                if not self.env.context.get('sync_from_variant'):
                    update_vals = {}
                    if 'list_price' in vals and template.list_price != variant.list_price:
                        update_vals['list_price'] = template.list_price
                    if 'binding_type' in vals and template.binding_type != variant.binding_type:
                        update_vals['binding_type'] = template.binding_type.id
                    if 'publication_date' in vals and template.publication_date != variant.publication_date:
                        update_vals['publication_date'] = template.publication_date
                    if 'last_edition' in vals and template.last_edition != variant.last_edition:
                        update_vals['last_edition'] = template.last_edition
                    if 'pages' in vals and template.pages != variant.pages:
                        update_vals['pages'] = template.pages
                    if 'paper_gsm' in vals and template.paper_gsm != variant.paper_gsm:
                        update_vals['paper_gsm'] = template.paper_gsm
                    if 'height' in vals and template.height != variant.height:
                        update_vals['height'] = template.height
                    if 'width' in vals and template.width != variant.width:
                        update_vals['width'] = template.width
                    if 'weight' in vals and template.weight != variant.weight:
                        update_vals['weight'] = template.weight
                    if 'description_ecommerce' in vals and template.description_ecommerce != variant.description_ecommerce:
                        update_vals['description_ecommerce'] = template.description_ecommerce
                    if 'length' in vals and template.length != variant.length:
                        update_vals['length'] = template.length


                    if update_vals:
                        variant.with_context(sync_from_template=True).write(update_vals)
        return res


    # @api.onchange('categ_id')

    @api.depends('categ_id', 'categ_id.parent_id', 'categ_id.complete_name')
    def _compute_is_book(self):
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

    def _sync_public_categories_from_partners(self):
        """Sync public_categ_ids based on author_ids and publisher_ids."""
        PublicCategory = self.env['product.public.category']

        for template in self:
            # Collect current writer/publisher-linked categories
            current_writer_categs = template.public_categ_ids.filtered(
                lambda c: c.related_writer_id
            )
            current_publisher_categs = template.public_categ_ids.filtered(
                lambda c: c.related_publisher_id
            )

            # Build expected categories from current author_ids
            expected_writer_categs = PublicCategory.search([
                ('related_writer_id', 'in', template.author_ids.ids)
            ])

            # Build expected categories from current publisher_ids
            expected_publisher_categs = PublicCategory.search([
                ('related_publisher_id', 'in', template.publisher_ids.ids)
            ])

            # Compute what to add and remove
            to_add = (expected_writer_categs - current_writer_categs) | \
                     (expected_publisher_categs - current_publisher_categs)
            to_remove = (current_writer_categs - expected_writer_categs) | \
                        (current_publisher_categs - expected_publisher_categs)

            if to_add or to_remove:
                commands = [(4, categ.id) for categ in to_add] + \
                           [(3, categ.id) for categ in to_remove]
                template.with_context(skip_categ_sync=True).write(
                    {'public_categ_ids': commands}
                )

    # -----------------------------------------------
    # Update your existing create() override
    # -----------------------------------------------

    def create(self, vals):
        res = super().create(vals)

        # Existing variant sync logic
        product = self.env['product.product'].search([('product_tmpl_id', '=', res.id)])
        sync_dict = {}
        for key in vals:
            if isinstance(key, str) and key in product._fields:
                sync_dict[key] = vals[key]
        product.write(sync_dict)

        # NEW: sync ecommerce categories after record has an ID
        res._sync_public_categories_from_partners()

        return res

    # -----------------------------------------------
    # Update your existing write() override
    # -----------------------------------------------

    def write(self, vals):
        res = super().write(vals)

        # Existing variant sync logic (your current code stays here unchanged)
        for template in self:
            if len(template.product_variant_ids) == 1:
                ...  # your existing sync logic

        # NEW: sync ecommerce categories only when authors/publishers changed
        if ('author_ids' in vals or 'publisher_ids' in vals) and \
                not self.env.context.get('skip_categ_sync'):
            self._sync_public_categories_from_partners()

        return res

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     search_domain = [('name', operator, name)]  # Default search in the current language
    #
    #     # Get all active languages
    #     active_langs = self.env['res.lang'].search([('active', '=', True)])
    #     product_ids = set()
    #
    #     # Search product names in all active languages
    #     for lang in active_langs:
    #         translated_products = self.with_context(lang=lang.code).search([('name', operator, name)], limit=limit)
    #         product_ids.update(translated_products.ids)
    #
    #     # Add translated product IDs to the search domain
    #     if product_ids:
    #         search_domain = ['|'] + search_domain + [('id', 'in', list(product_ids))]
    #
    #     # Search for products
    #     products = self.search(search_domain + args, limit=limit)
    #
    #     # Return product names manually
    #     return [(prod.id, prod.name) for prod in products]  # Odoo 18 workaround


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
    pages = fields.Integer("Page")
    paper_gsm = fields.Integer("GSM")
    length = fields.Float("lenght")
    height = fields.Float("Height")
    width = fields.Float("Width")
    weight = fields.Float("Weight")
    description_ecommerce = fields.Html(
            string="eCommerce Description",
            translate=html_translate,
            sanitize_overridable=True,
            sanitize_attributes=False,
            sanitize_form=False,
        )
    # set variant fields with same value while only one variant
    def write(self, vals):
        res = super().write(vals)
        for variant in self:
            template = variant.product_tmpl_id
            if len(template.product_variant_ids) == 1:
                if not self.env.context.get('sync_from_template'):
                    update_vals = {}
                    if 'list_price' in vals and template.list_price != variant.list_price:
                        update_vals['list_price'] = variant.list_price
                    if 'binding_type' in vals and template.binding_type != variant.binding_type:
                        update_vals['binding_type'] = variant.binding_type.id
                    if 'publication_date' in vals and template.publication_date != variant.publication_date:
                        update_vals['publication_date'] = variant.publication_date
                    if 'last_edition' in vals and template.last_edition != variant.last_edition:
                        update_vals['last_edition'] = variant.last_edition
                    if 'pages' in vals and template.pages != variant.pages:
                        update_vals['pages'] = variant.pages
                    if 'paper_gsm' in vals and template.paper_gsm != variant.paper_gsm:
                        update_vals['paper_gsm'] = variant.paper_gsm
                    if 'length' in vals and template.length != variant.length:
                        update_vals['length'] = variant.length
                    if 'height' in vals and template.height != variant.height:
                        update_vals['height'] = variant.height
                    if 'width' in vals and template.width != variant.width:
                        update_vals['width'] = variant.width
                    if 'weight' in vals and template.weight != variant.weight:
                        update_vals['weight'] = variant.weight
                    if 'description_ecommerce' in vals and template.description_ecommerce != variant.description_ecommerce:
                        update_vals['description_ecommerce'] = variant.description_ecommerce
                    if update_vals:
                        template.with_context(sync_from_variant=True).write(update_vals)
        return res


    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     # multi langual search is working
    #     user_lang = self.env.context.get('lang', 'en_US')
    #     domain = args or []
    #     positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
    #     is_positive = operator not in expression.NEGATIVE_TERM_OPERATORS
    #     matched_ids = set()
    #
    #     # Search in all active languages
    #     active_langs = self.env['res.lang'].search([('active', '=', True)]).mapped('code')
    #
    #     for lang_code in active_langs:
    #         env_lang = self.with_context(lang=lang_code)
    #
    #         # Try exact code/barcode matches first (fast lookup)
    #         products = env_lang.search(expression.AND([domain, [('default_code', '=', name)]]), limit=limit)
    #         products |= env_lang.search(expression.AND([domain, [('barcode', '=', name)]]), limit=limit)
    #
    #         if not products and is_positive:
    #             products = env_lang.search(expression.AND([domain, [('default_code', operator, name)]]),
    #                                        limit=limit)
    #             limit_rest = limit and limit - len(products)
    #             if limit_rest is None or limit_rest > 0:
    #                 products |= env_lang.search(
    #                     expression.AND([
    #                         domain,
    #                         [('id', 'not in', list(matched_ids)), ('name', operator, name)]
    #                     ]), limit=limit_rest
    #                 )
    #         elif not products and not is_positive:
    #             products = env_lang.search(
    #                 expression.AND([
    #                     domain,
    #                     [('name', operator, name), '|', ('default_code', operator, name),
    #                      ('default_code', '=', False)]
    #                 ]), limit=limit
    #             )
    #
    #         matched_ids.update(products.ids)
    #
    #         # Stop early if limit is reached
    #         if limit and len(matched_ids) >= limit:
    #             break
    #
    #     # Final result in user's language
    #     final_products = self.browse(list(matched_ids)).with_context(lang=user_lang)
    #     return [(product.id, product.display_name) for product in final_products.sudo()]


class ProductGenre(models.Model):
    _name = 'product.genre'
    _description = 'Book Genre'
    name = fields.Char(string="Genre", required=True ,translate=True)
    description = fields.Char(string="Description", required=True,translate=True)

# class ProductPublicCategory(models.Model):
#     _inherit='product.public.category'
#     _description='this modules adds product public categories for writer and publishers'
#     is_published=fields.Boolean("Is Published")
#     related_writer_id=fields.Many2one('res.partner',"Writer")
#     related_publisher_id=fields.Many2one('res.partner',"Publisher")

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
    is_published = fields.Boolean("Is Published", default=False)
    related_writer_id=fields.Many2one('res.partner',"Writer")
    related_publisher_id=fields.Many2one('res.partner',"Publisher")



