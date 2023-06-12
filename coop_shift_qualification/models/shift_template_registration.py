from odoo import api, models, _
from odoo.exceptions import ValidationError


class ShiftTemplateRegistration(models.Model):
    _inherit = "shift.template.registration"

    @api.multi
    def update_leaders(self, partners, action='add'):
        if not partners:
            return
        for reg in self:
            tmpl = reg.shift_template_id
            shifts = tmpl.shift_ids.filtered(
                lambda s: s.state != "done")
            for partner in partners:
                if action == 'add':
                    if reg.is_current_participant and \
                            partner.is_qual_leader:
                        warn_msg = partner._get_leader_ftop_warning(tmpl)
                        if warn_msg:
                            raise ValidationError(warn_msg)

                        tmpl.user_ids |= partner
                        tmpl.removed_user_ids -= partner
                        for shift in shifts:
                            shift.user_ids |= partner
                elif action == 'del':
                    if partner in tmpl.user_ids:
                        tmpl.user_ids -= partner
                        tmpl.removed_user_ids |= partner
                        for shift in shifts:
                            shift.user_ids -= partner

    @api.model
    def create(self, vals):
        regs = super(ShiftTemplateRegistration, self).create(vals)
        for reg in regs:
            reg.update_leaders(reg.partner_id)
        return regs

    @api.multi
    def write(self, vals):
        res = True
        if vals.get("partner_id") or vals.get("shift_template_id"):
            for reg in self:
                reg.update_leaders(reg.partner_id, action='del')
                res = super(ShiftTemplateRegistration, reg).write(vals)
                reg.update_leaders(reg.partner_id)
        else:
            res = super(ShiftTemplateRegistration, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        res = True
        for reg in self:
            reg.update_leaders(reg.partner_id, action='del')
            res = super(ShiftTemplateRegistration, reg).unlink()
        return res
