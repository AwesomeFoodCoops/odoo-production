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

        if not self or self._is_admin():
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

    @api.multi
    def check_access_ui(self, res_model):
        """
        Check group current user to hide buttons / bars
        @return: dict({
            # For Form
            "o_cp_sidebar": True / False,
            "o_chatter_topbar": True / False,
            "o_cp_buttons": True / False,

            # For list
            "o_button_import": True / False,
            # For list: when select the checkbox
            "o_cp_sidebar": True / False,
        })

        """
        result = self.check_access_buttons(res_model)
        resp = {
            "o_cp_sidebar": True,
            "o_chatter_topbar": True,
            "o_cp_buttons": True,
            "o_button_import": True,
            # "o_cp_sidebar": True
            "result": result
        }
        if result == 'lecture_group_partner':
            resp["o_cp_sidebar"] = False
            resp["o_chatter_topbar"] = False
            resp["o_cp_buttons"] = False
        elif result == 'presence_group_partner':
            resp["o_cp_sidebar"] = False
            resp["o_chatter_topbar"] = False
            resp["o_cp_buttons"] = False
        elif result == 'saisie_group_partner':
            resp["o_cp_sidebar"] = False
            resp["o_chatter_topbar"] = False
        elif result == 'presence_group_shift':
            resp["o_cp_sidebar"] = False
            resp["o_chatter_topbar"] = False
            resp["o_cp_buttons"] = True
        elif result == 'saisie_group_shift':
            resp["o_cp_sidebar"] = False
            resp["o_chatter_topbar"] = False
        elif result == 'saisie_group_leave':
            resp["o_cp_sidebar"] = False
            resp["o_chatter_topbar"] = False
        # else:
        #     resp["o_cp_sidebar"] = True
        #     resp["o_chatter_topbar"] = True
        #     resp["o_cp_buttons"] = True
        if result:
            resp["o_button_import"] = False
        self.check_access_ui_super_groups(resp)
        return resp

    @api.multi
    def check_access_ui_super_groups(self, resp):
        if self.has_group(
            'coop_membership.group_membership_chatter_topbar'):
            resp["o_chatter_topbar"] = True
        if self.has_group(
            'coop_membership.group_membership_action_sidebar'):
            resp["o_cp_sidebar"] = True
