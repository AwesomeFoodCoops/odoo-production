from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Function trigger to
            - Change the email of current user to the email of
            the assigned partner
        """
        self.login = self.partner_id and self.partner_id.email or ''

    @api.multi
    def check_access_buttons(self, res_model):
        """
        Check group current user to hide buttons

        """
        presence_group = self.has_group(
            'coop_membership.group_membership_bdm_presence')
        lecture_group = self.has_group(
            'coop_membership.group_membership_bdm_lecture')
        saisie_group = self.has_group(
            'coop_membership.group_membership_bdm_saisie')

        if self._is_admin():
            return False
        elif res_model == 'res.partner':
            if saisie_group:
                return 'saisie_group_partner'
            if presence_group:
                return 'presence_group_partner'
            if lecture_group:
                return 'lecture_group_partner'
        elif res_model == 'shift.shift':
            if presence_group:
                return 'presence_group_shift'
            if lecture_group:
                return 'lecture_group_shift'
            if saisie_group:
                return 'saisie_group_shift'
        elif res_model == "shift.leave":
            if saisie_group:
                return 'saisie_group_leave'
        # elif res_model == "shift.registration":
        #     if saisie_group:
        #         return 'saisie_group_registration'
        elif res_model == "shift.template.registration.line":
            if saisie_group:
                return 'saisie_group_template_registration_line'
        elif res_model == "shift.extension":
            if saisie_group:
                return 'saisie_group_extension'
        else:
            return False
