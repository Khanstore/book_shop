from odoo import http
from odoo.http import request

class ProductVariantPages(http.Controller):
    @http.route('/get_product_pages', type='json', auth='public', website=True)
    def get_product_pages(self, **kwargs):
        product_id = int(kwargs.get('product_id', 0))
        product = request.env['product.product'].browse(product_id)
        return {
            'publication':product.publication_date,
            'edition':product.last_edition,
            'binding': product.binding_type.name if product.binding_type else '',
            'pages': product.pages or 0}
