# -*- coding: utf-8 -*-
# Copyright (C) 2015-Today: Smile (<http://www.smile.fr>)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class WizardUseTheoriticalPrice(models.TransientModel):
    _name = 'wizard.use.theoritical.price'

    # Custom Section
    @api.multi
    def apply(self):
        template_obj = self.env['product.template']
        for wizard in self:
            templates = template_obj.browse(
                self._context.get('active_ids', []))
            for template in templates:
                if template.has_theoritical_price_different:
                    template.list_price = template.theoritical_price
