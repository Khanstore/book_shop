# -*- coding: utf-8 -*-
###################################################################################
#
#    Eagle ERP Ltd.
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
import base64
import urllib

from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.tools.translate import html_translate


class ProductPen(models.Model):
    _name = 'product.pen'
    _inherits = {'product.template': 'product_tmpl_id'}

    product_tmpl_id = fields.Many2one('product.template', required=True, ondelete='cascade')
    ink_color = fields.Char('Ink Color')
    product_color = fields.Char('Product Color')
    tip_size = fields.Char('Tip Size')
    design = fields.Char('Design')
    tip_type = fields.Char('Tip Type')
    use_type = fields.Char('Use Type')
    material_type = fields.Char('Material Type')
    writing_experience = fields.Char('Writing Experience')
    feature = fields.Char('Feature')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    printed_name = fields.Char('Name')
    is_book = fields.Boolean(
        "Is A Book",
        compute='_compute_is_book',
        store=True,
    )
    isbn = fields.Char(string="ISBN")
    author_ids = fields.Many2many(
        comodel_name="res.partner",
        relation='author_book_rel',
        column1='author_of',
        column2="author_ids",
        string="Author"
    )
    publisher_ids = fields.Many2many(
        comodel_name="res.partner",
        relation='publisher_book_rel',
        column1='publisher_of',
        column2='publisher_ids',
        string="Publisher"
    )
    publication_date = fields.Char(string="Publication Date")
    last_edition = fields.Char(string="Last Edition")
    genre = fields.Many2one('product.genre', string="Genre")
    binding_type = fields.Many2one("book.binding.type")
    pages = fields.Integer(string="Page")
    paper_gsm = fields.Integer("GSM")
    paper_color = fields.Many2one("book.paper.color", string="Colour")
    paper_quality = fields.Many2one("paper.quality", string="Paper Quality")
    length = fields.Float("lenght")
    height = fields.Float("Height")
    width = fields.Float("Width")

    @api.depends('categ_id', 'categ_id.parent_id', 'categ_id.complete_name')
    def _compute_is_book(self):
        for rec in self:
            category = rec.categ_id
            rec.is_book = False
            while category:
                if category.get_external_id().get(category.id) == 'book_shop.product_category_book':
                    rec.is_book = True
                    break
                category = category.parent_id if category.parent_id else False

    @api.onchange('author_ids')
    def writer_ids_onchange(self):
        ecom_categ = self.public_categ_ids
        for rec in ecom_categ:
            if rec.related_writer_id:
                self.public_categ_ids = [(3, rec._origin.id)]
        for line in self.author_ids:
            new_ecom_categ = self.env['product.public.category'].search(
                [('related_writer_id', '=', line._origin.id)]
            )
            self.public_categ_ids = [(4, new_ecom_categ.id)]

    @api.onchange('publisher_ids')
    def publisher_ids_onchange(self):
        ecom_categ = self.public_categ_ids
        for rec in ecom_categ:
            if rec.related_publisher_id:
                self.public_categ_ids = [(3, rec._origin.id)]
        for line in self.publisher_ids:
            new_ecom_categ = self.env['product.public.category'].search(
                [('related_publisher_id', '=', line._origin.id)]
            )
            self.public_categ_ids = [(4, new_ecom_categ.id)]

    def _sync_public_categories_from_partners(self):
        """Sync public_categ_ids based on author_ids and publisher_ids."""
        PublicCategory = self.env['product.public.category']

        for template in self:
            current_writer_categs = template.public_categ_ids.filtered(
                lambda c: c.related_writer_id
            )
            current_publisher_categs = template.public_categ_ids.filtered(
                lambda c: c.related_publisher_id
            )

            expected_writer_categs = PublicCategory.search([
                ('related_writer_id', 'in', template.author_ids.ids)
            ])
            expected_publisher_categs = PublicCategory.search([
                ('related_publisher_id', 'in', template.publisher_ids.ids)
            ])

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

    def create(self, vals):
        res = super().create(vals)

        # Ensure single variant updates pass context to bypass stock valuation triggers
        if len(res.product_variant_ids) == 1:
            product = res.product_variant_id
            sync_dict = {}
            for key in vals:
                if isinstance(key, str) and key in product._fields:
                    sync_dict[key] = vals[key]
            if sync_dict:
                product.with_context(
                    sync_from_template=True,
                    disable_auto_svl=True
                ).write(sync_dict)

        res._sync_public_categories_from_partners()
        return res

    def write(self, vals):
        res = super().write(vals)

        # Skip sync if this write was initiated from variant to avoid recursion loops
        if not self.env.context.get('sync_from_variant'):
            for template in self:
                if len(template.product_variant_ids) == 1:
                    variant = template.product_variant_ids[0]
                    update_vals = {}

                    fields_to_sync = [
                        'list_price', 'binding_type', 'publication_date', 'last_edition',
                        'pages', 'paper_gsm', 'height', 'width', 'weight',
                        'description_ecommerce', 'length'
                    ]

                    for field in fields_to_sync:
                        if field in vals:
                            val = getattr(template, field)
                            var_val = getattr(variant, field)

                            # Handle relational fields
                            if hasattr(val, 'id'):
                                val = val.id
                            if hasattr(var_val, 'id'):
                                var_val = var_val.id

                            if val != var_val:
                                update_vals[field] = val

                    if update_vals:
                        variant.with_context(
                            sync_from_template=True,
                            disable_auto_svl=True
                        ).write(update_vals)

        if ('author_ids' in vals or 'publisher_ids' in vals) and \
                not self.env.context.get('skip_categ_sync'):
            self._sync_public_categories_from_partners()

        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

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

    def write(self, vals):
        res = super().write(vals)

        # Skip sync if write was initiated from template
        if not self.env.context.get('sync_from_template'):
            for variant in self:
                template = variant.product_tmpl_id
                if len(template.product_variant_ids) == 1:
                    update_vals = {}

                    fields_to_sync = [
                        'list_price', 'binding_type', 'publication_date', 'last_edition',
                        'pages', 'paper_gsm', 'height', 'width', 'weight',
                        'description_ecommerce', 'length'
                    ]

                    for field in fields_to_sync:
                        if field in vals:
                            val = getattr(variant, field)
                            tmpl_val = getattr(template, field)

                            # Handle relational fields
                            if hasattr(val, 'id'):
                                val = val.id
                            if hasattr(tmpl_val, 'id'):
                                tmpl_val = tmpl_val.id

                            if val != tmpl_val:
                                update_vals[field] = val

                    if update_vals:
                        template.with_context(
                            sync_from_variant=True,
                            disable_auto_svl=True
                        ).write(update_vals)
        return res


class ProductGenre(models.Model):
    _name = 'product.genre'
    _description = 'Book Genre'
    name = fields.Char(string="Genre", required=True, translate=True)
    description = fields.Char(string="Description", required=True, translate=True)


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
    name = fields.Char("Binding Type")
    description = fields.Char("description")
    image = fields.Binary("Image", help='Image for binding Type.')


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'
    _description = 'this modules adds product public categories for writer and publishers'
    is_published = fields.Boolean("Is Published", default=False)
    product_tmpl_count = fields.Integer(string="Product Count", compute="get_product_tmpl_count", store=True)
    related_writer_id = fields.Many2one('res.partner', "Writer")
    related_publisher_id = fields.Many2one('res.partner', "Publisher")

    def get_product_tmpl_count(self):
        for rec in self:
            rec.product_tmpl_count = self.env['product.template'].search_count([
                ('public_categ_ids', 'in', rec.id)
            ])