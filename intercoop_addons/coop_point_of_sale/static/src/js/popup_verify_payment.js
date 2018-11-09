/*
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
*/

odoo.define('coop_point_of_sale.popup_screen_payment', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var _t = core._t;

    screens.PaymentScreenWidget.include({
        click_paymentmethods: function(id) {
            var self = this;

            var payable_to = '';
            var account_journal_ids = [];
            if (this.pos.config_info_settings.payable_to){
                payable_to = this.pos.config_info_settings.payable_to;
            }

            if (this.pos.config_info_settings.account_journal_ids){
                account_journal_ids = this.pos.config_info_settings.account_journal_ids;
            }

            /*var  = this.pos.config_settings ? this.pos.config_settings.receipt_options : false;*/

            var thanks_message = _("Merci de vérifier sur le chèque :"); 
            var lemon = _("le montant"); 
            var la_date = _("la date"); 
            var order_messages = _("l'ordre: " + payable_to);
            var signature = _("la présence d'une signature");


            if(account_journal_ids.includes(id)){
                this.gui.show_popup('okpopup',{
                'title': _('Vérifier sur le chèque'),
                'thanks_message': thanks_message,
                'lemon': lemon,
                'la_date': la_date,
                'order_messages': order_messages,
                'signature': signature,

            });
            }

            this._super.apply(this, arguments);
        },
    });


});
