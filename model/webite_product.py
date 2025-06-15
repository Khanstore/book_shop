from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route

class WebsiteSaleCustom(WebsiteSale):

    @route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        # Filter active variants only for 'Shariful Guide'
        # if product.name == 'Shariful Guide':
        product = product.with_context(active_test=True)
        product.product_variant_ids = product.product_variant_ids.filtered(lambda v: v.active)
        return super().product(product, category, search, **kwargs)
