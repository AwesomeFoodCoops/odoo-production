
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def name_get(self):
        """Return the product name without ref when the
        name_get is called from order planning form
        """
        res = []
        if self.env.context.get('partner_display_only_ref'):
            for record in self:
                res.append((record['id'], record.ref or record.name))
        else:
            res = super(ResPartner, self).name_get()

        return res
