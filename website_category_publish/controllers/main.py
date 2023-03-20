from odoo.osv import expression
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteCategoryPublish(WebsiteSale):
    ''' Overwrite this controller to support category published filters '''

    def _get_search_domain(self, search, category, attrib_values):
        domain = super()._get_search_domain(search, category, attrib_values)
        args = [
            ("is_categ_published", "=", True)
        ]
        domain = expression.AND([args, domain])
        return domain

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        response = super(WebsiteCategoryPublish, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post)
        categories = response.qcontext['categories']
        categories = categories.filtered(lambda c: c.is_published)
        response.qcontext['categories'] = categories
        return response
