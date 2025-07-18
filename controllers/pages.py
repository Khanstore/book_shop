from odoo import http
from odoo.http import request

class ProductVariantPages(http.Controller):
    @http.route('/get_product_pages', type='json', auth='public', website=True)
    def get_product_pages(self, **kwargs):
        product_id = int(kwargs.get('product_id', 0))
        product = request.env['product.product'].sudo().browse(product_id)
        paper=""
        if product.paper_gsm and product.paper_gsm > 0:
            paper += f"{product.paper_gsm} Gram"
        if product.paper_color and product.paper_color.id > 0:
            paper += f" {product.paper_color.name}"
        if product.paper_quality and product.paper_quality.id > 0:
            paper += f" {product.paper_quality.name}"
        paper = paper.strip()


        return {
            'publication':product.publication_date,
            'edition':product.last_edition,
            'binding': product.binding_type.name if product.binding_type else '',
            'paper': paper,
            'pages': product.pages or 0}
