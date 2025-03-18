
from odoo import http

class BookShop(http.Controller):
    @http.route('/books', type='http', auth='public', website=True)
    def render_webpage(self, **kwargs):
        return http.request.render('book_shop.book_shop', {
            'message': 'Welcome to My Web Page Book Shop!',
        })