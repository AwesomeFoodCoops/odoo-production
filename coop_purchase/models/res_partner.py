from lxml import etree
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    show_discount = fields.Boolean("Show discounts on update prices")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type,
                                      toolbar=toolbar, submenu=submenu)
        if view_type == "form":
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//field[@name='debit']"):
                node.addnext(etree.Element("field", name="show_discount"))
                res["fields"].update(
                    self.fields_get(allfields=["show_discount"])
                )
            res["arch"] = etree.tostring(doc)
        return res
