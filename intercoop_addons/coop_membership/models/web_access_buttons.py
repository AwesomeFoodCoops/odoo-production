# -*- coding: utf-8 -*-

from openerp import models, api, exceptions
from openerp import SUPERUSER_ID


@api.multi
def check_access_buttons(self):
    """
    Check group current user to hide buttons

    """
    presence_group = self.env.user.has_group(
        'coop_membership.group_membership_bdm_presence')
    lecture_group = self.env.user.has_group(
        'coop_membership.group_membership_bdm_lecture')
    saisie_group = self.env.user.has_group(
        'coop_membership.group_membership_bdm_saisie')
    deceased_group = self.env.user.has_group(
        'coop_membership.group_membership_view_partner_deceased')
    if self.env.user.id == SUPERUSER_ID:
        return False
    elif self._name == 'res.partner':
        if presence_group:
            return 'presence_group_partner'
        if lecture_group and not deceased_group:
            return 'lecture_group_partner'
        if saisie_group:
            return 'saisie_group_partner'
    elif self._name == 'shift.shift':
        if presence_group:
            return 'presence_group_shift'
        if lecture_group and not deceased_group:
            return 'lecture_group_shift'
        if saisie_group:
            return 'saisie_group_shift'
    elif self._name == "shift.leave":
        if saisie_group:
            return 'saisie_group_leave'
    elif self._name == "shift.registration":
        if saisie_group:
            return 'saisie_group_registration'
    elif self._name == "shift.template.registration.line":
        if saisie_group:
            return 'saisie_group_template_registration_line'
    elif self._name == "shift.extension":
        if saisie_group:
            return 'saisie_group_extension'
    else:
        return False


models.BaseModel.check_access_buttons = check_access_buttons
