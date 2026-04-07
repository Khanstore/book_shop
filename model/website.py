from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

# class WebsiteSaleMultiLang(WebsiteSale):
#     @http.route(['/shop/search'], type='http', auth="public", website=True, sitemap=False)
#     def shop_search(self, search='', **kwargs):
#         """
#         Override Odoo website search to support multi-language product names.
#         """
#         domain = [('sale_ok', '=', True)]
#         if search:
#             product_ids = set()
#             active_langs = request.env['res.lang'].sudo().search([('active', '=', True)])
#
#             # Search product names in all active languages
#             for lang in active_langs:
#                 translated_products = request.env['product.template'].with_context(lang=lang.code).sudo().search([
#                     ('name', 'ilike', search)
#                 ])
#                 product_ids.update(translated_products.ids)
#
#             # Update search domain with multilingual product IDs
#             if product_ids:
#                 domain = ['|', ('name', 'ilike', search), ('id', 'in', list(product_ids))]
#
#         # Call the original Odoo shop page with modified domain
#         return super().shop(**kwargs, search=search, **{'domain': domain})
