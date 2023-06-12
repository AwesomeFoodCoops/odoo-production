from odoo import api, models, _
from odoo.exceptions import ValidationError


class ShiftTemplate(models.Model):
    _inherit = "shift.template"

    @api.multi
    def update_qualification(self, partners, action='add', raise_error=True):
        if not partners:
            return
        lead_quals = self.env["res.partner.qualification"].search([
            ("is_leader", "=", True)
        ])
        if not lead_quals:
            return
        for tmpl in self:
            if tmpl.is_ftop:
                continue
            regs = tmpl.current_registration_ids
            for partner in partners:
                if action == 'add':
                    if partner.is_qual_leader:
                        continue
                    reg = regs.filtered(
                        lambda r: r.partner_id == partner)
                    if not reg:
                        continue
                    warn_msg = partner._get_leader_ftop_warning(tmpl)
                    if warn_msg:
                        if raise_error:
                            raise ValidationError(warn_msg)
                        else:
                            continue
                    partner.qualification_ids |= lead_quals[0]

                elif action == 'del':
                    curr_tmpls = partner.template_ids - self
                    if curr_tmpls:
                        continue
                    partner.qualification_ids -= lead_quals

    @api.model
    def create(self, vals):
        tmpls = super(ShiftTemplate, self).create(vals)
        for tmpl in tmpls:
            tmpl.update_qualification(tmpl.mapped("user_ids"))
        return tmpls

    @api.multi
    def write(self, vals):
        res = True
        if vals.get("user_ids") or vals.get("shift_type_id"):
            for tmpl in self:
                curr_partners = tmpl.mapped("user_ids")
                res = super(ShiftTemplate, tmpl).write(vals)
                new_partners = tmpl.mapped("user_ids")
                to_add = new_partners - curr_partners
                to_del = curr_partners - new_partners
                tmpl.update_qualification(to_del, action='del')
                tmpl.update_qualification(to_add)
        else:
            res = super(ShiftTemplate, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        res = True
        for tmpl in self:
            tmpl.update_qualification(tmpl.mapped("user_ids"), action='del')
            res = super(ShiftTemplate, tmpl).unlink()
        return res
