odoo.define('coop_membership.sidebar_access_button', function(require) {
    "use strict";

    var core = require('web.core');
    var data = require('web.data');
    var framework = require('web.framework');
    var sideWidget = require('web.Sidebar');
    var Model = require('web.Model');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    var QWeb = core.qweb;


    var sidebar = sideWidget.include({


        redraw: function() {

            var self = this;
            this._super.apply(this, arguments);
            if (this.getParent()) {
                var view = this.getParent();

                this.getParent().dataset.call('check_access_buttons_action',
                            [this.getParent().dataset.ids])
                .then(function(result) {
                    self.hide_buttons(result);
                });
            }
        },

        hide_buttons: function(result) {
            if (result){
                self.$('.oe_sidebar_add_attachment').parent().parent().hide();
                self.$('.oe_sidebar_relate').parent().parent().hide();
                self.$('.oe_sidebar_action').parent().parent().hide();
            }
        }

    });

    
});
