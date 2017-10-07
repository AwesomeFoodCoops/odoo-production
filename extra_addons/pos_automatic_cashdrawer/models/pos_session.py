
# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Aurélien DUMAINE (http://www.dumaine.me)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _get_automatic_cashdrawer_content_inventory(self):
        proxy = self.pool['proxy.action.helper'].create()
        posbox_address = self.config_id.proxy_ip
        if posbox_address[:4] != 'http': #if https, it's also OK
          posbox_address += 'http://'
        #check cashlogy initialization
        url = posbox_ip+'/hw_proxy/automatic_cashdrawer_connection_check'
        cashlogy_cnnector_ip_adress = self.config_id.iface_automatic_cashdrawer_ip_address
        cashlogy_connector_tcp_port = self.config_id.iface_automatic_cashdrawer_tcp_port
        request = {'url': url,'params':{connection_info:{'ip_address':cashlogy_cnnector_ip_adress,'tcp_port':cashlogy_connector_tcp_port}}}
        init_cashlogy = prox.send_proxy([request])
        # get cashlogy content inventory
        url = posbox_ip+'/hw_proxy/automatic_cashdrawer_content_inventory'
        request = {'url': url,'params':''}
        inventory = prox.send_proxy([request])
        #inventory = {'value_of_coin_bill':number_coin_bill,...}
        #inventory = {'2.00':4,'50.0':3} => 2€x4 + 50€x3 => 158€
        return inventory
"""
    def wkf_action_opening_control(self, cr, uid, ids, context=None):
        result = dict()
        for session in self.browse(cr, uid, ids, context=context):
            if self.config.id.automatic_cashdrawer == True :
                cash_inventory = self._get_automatic_cashdrawer_content_inventory()
                if cash_inventory==None :
                      result[session.id]=erromessage
                for i in cash_inventory:
                     #add to opening balance
                if openning_balance = 0
                      result[session.id]=erromessage
        result[session.id]=True
        return super(pos_session, self).wkf_action_opening_control()

    def wkf_action_closing_control(self, cr, uid, ids, context=None):
        result = dict()
        if self.config.id.automatic_cashdrawer == True :
            cash_inventory = self._get_automatic_cashdrawer_content_inventory()
            if cash_inventory==None :
                  result[session.id]=erromessage
            for i in cash_inventory:
                 #add to closing balance
        result[session.id]=True
        return super(pos_session, self).wkf_action_closing_control()
"""
    #TODO : add a object bank.statement.cash.balance.detail that have "value/number_opening/total_openning/number_closing/total_closing"
    #TODO : add field on bank.statement.cash_balance_detail_ids that trigger computation of balance_start and balance_end_real
    #TODO : add button to call the backend on session form.
    #TODO : add a pos user right to hide "Close" button from the front end
    #TODO : in the pos.session resume, add lines bellow cash summary with detail of coins/bills number @oenning and @closing
