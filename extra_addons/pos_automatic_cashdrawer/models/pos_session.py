
# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Aurélien DUMAINE (http://www.dumaine.me)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    #TODO : override "launch or resume session" function : if there is an automatic cashdrawer 
    # configured on this pos_config, do not launch front-end UI if there is no coin/notes record on this session
    
    def _get_automatic_cashdraer_content_inventory_button(self):
        proxy = self.pool['proxy.action.helper'].create()
        posbox_address = self.config_id.proxy_ip
        if posbox_address[:4] != 'http': #if https, it's also OK
          posbox_address += 'http://'
        #check cashlogy initialization
        url = posbox_ip+'/hw_proxy/automatic_cashdrawer_connection_check'
        cashlogy_cnnector_ip_adress = self.config_id.iface_automatic_cashdrawer_ip_address
        cashlogy_connector_tcp_port = self.config_id.iface_automatic_cashdrawer_tcp_port
        request = {'url': url,'params':{connection_info:{'ip_address':cashlogy_cnnector_ip_adress,'tcp_port',cashlogy_connector_tcp_port}}}
        init_cashlogy = prox.send_proxy([request])
        # get cashlogy content inventory
        url = posbox_ip+'/hw_proxy/automatic_cashdrawer_content_inventory'
        request = {'url': url,'params':''}
        inventory = prox.send_proxy([request])
        # TODO : call "add money" wizzard with inventory as context
        # OR create notes/coin lines use this function to override the "launch/resume function (UI launcher)
