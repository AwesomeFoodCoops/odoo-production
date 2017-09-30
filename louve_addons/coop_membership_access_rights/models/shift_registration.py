# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class ShiftRegistration(models.Model):
    _inherit = "shift.registration"

    related_shift_state = fields.Selection(related="shift_id.state",
                                           store=False,
                                           string="Shift State")

    @api.multi
    @api.onchange("shift_id")
    def onchange_shift_id(self):
        # Use the context value for default
        is_standard_ticket = self.env.context.get("is_standard_ticket", False)
        ticket_type_product = False
        if is_standard_ticket:
            ticket_type_product = \
                self.env.ref("coop_shift.product_product_shift_standard")
        else:
            ticket_type_product = \
                self.env.ref("coop_shift.product_product_shift_ftop")
        for reg in self:
            reg.shift_ticket_id = reg.shift_id.shift_ticket_ids.filtered(
                lambda t: t.product_id == ticket_type_product)

    @api.model
    def create(self, vals):
        '''
        @Function overided to control the creation of the registration
            - Do not allow member with Up to date status register make up
            in a ABCD shift on a ABCD tickets
        '''
        res = super(ShiftRegistration, self).create(vals)
        res.checking_shift_attendance()
        return res

    @api.model
    def write(self, vals):
        res = super(ShiftRegistration, self).write(vals)
        if 'template_created' in vals or 'shift_ticket_id' in vals:
            self.checking_shift_attendance()
        return res

    @api.multi
    def checking_shift_attendance(self):
        '''
        @Function to check the attendance:
            - Do not allow member with Up to date status registers make up
            in a ABCD shift on a ABCD tickets
        '''
        ignore_checking = \
            self.env.context.get('ignore_checking_attendance', False)
        if ignore_checking:
            return
        for shift_reg in self:
            shift_type = shift_reg.shift_id and \
                shift_reg.shift_id.shift_type_id
            uptodate_list = []
            if shift_type and not shift_type.is_ftop and \
                shift_reg.shift_type == 'standard' and \
                    not shift_reg.template_created and \
                    shift_reg.state not in ['replacing', 'replaced'] and \
                    shift_reg.partner_id.working_state == 'up_to_date':
                uptodate_list.append('- [%s] %s' % (
                    shift_reg.partner_id.barcode_base,
                    shift_reg.partner_id.name))
        if uptodate_list:
            raise UserError(_("Warning! You cannot enter make-ups of " +
                              "the following members " +
                              "as they are up-to-date: \n\n%s") %
                            '\n'.join(uptodate_list))
