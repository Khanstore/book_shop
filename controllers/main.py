# controllers/main.py
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.website.controllers.main import Home  # Inherit from Website controller




class CustomWebsiteController(Home):
    @http.route('/custom/page', type='http', auth='public', website=True)
    def custom_page(self, **kw):
        categories= request.env['product.category'].sudo().search([], order='name asc')
        return request.render('book_shop.custom_page_templates', {"categories":categories})

    @http.route([
        '/website/search',
        '/website/search/page/<int:page>',
        '/website/search/<string:search_type>',
        '/website/search/<string:search_type>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=False)
    def hybrid_list(self, page=1, search='', search_type='all', **kw):
        if not search:
            return request.render("website.list_hybrid")

        # Get the list of active languages
        languages = request.env['res.lang'].search([('active', '=', True)])

        # Prepare the search options to include all languages
        options = self._get_hybrid_search_options(**kw)
        

        # Modify the search function to search across all active languages
        search_results = []
        for lang in languages:
            # Set the language context for each search
            with request.env.cr.savepoint():
                request.env.context = dict(request.env.context, lang=lang.code)
                data = self.autocomplete(search_type=search_type, term=search, order='name asc', limit=500, max_nb_chars=200, options=options)
                search_results.extend(data.get('results', []))

        # Remove duplicates based on unique identifiers (e.g., 'id')
        seen_ids = set()
        unique_results = []
        for result in search_results:
            unique_field = result.get('website_url')  # Replace this line if 'id' is not the correct field
            if not unique_field:
                unique_results.append(result)
            elif unique_field not in seen_ids:
                seen_ids.add(unique_field)
                unique_results.append(result)

        search_count = len(unique_results)
        parts = data.get('parts', {})

        step = 50
        pager = portal_pager(
            url="/website/search/%s" % search_type,
            url_args={'search': search},
            total=search_count,
            page=page,
            step=step
        )

        results = unique_results[(page - 1) * step: page * step]

        values = {
            'pager': pager,
            'results': results,
            'parts': parts,
            'search': search,
            'fuzzy_search': data.get('fuzzy_search'),
            'search_count': search_count,
        }

        return request.render("website.list_hybrid", values)
