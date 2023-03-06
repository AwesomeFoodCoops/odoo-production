odoo.define('coop_membership.AccessButtons', function(require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var ListRenderer = require('web.ListRenderer');
    var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({

        _renderView: function() {
            var self = this;
            return this._super.apply(this, arguments)
                .then(function() {
                    self.check_hide_buttons()
                });
        },
        check_hide_buttons: function() {
            var self = this;
            var context = this.state.context;
            var res_model = this.state.model;
            this._rpc({
                model: 'res.users',
                method: 'check_access_buttons',
                args: [context.uid, res_model],
                context: context,
            }).then(function(result) {
                self.hide_button(result);
                session.user_has_group(
                    'coop_membership.group_membership_chatter_topbar'
                ).then(function (data) {
                    if (data) {
                        self.$('.o_chatter_topbar').show();
                    }
                });
            });
        },

        hide_button: function(result) {
            if (result == 'lecture_group_partner') {
                self.$('.o_cp_sidebar').hide();
                self.$('.o_chatter_topbar').hide();
                self.$('.o_cp_buttons').hide();
            } else if (result == 'presence_group_partner') {
                self.$('.o_cp_sidebar').hide();
                self.$('.o_chatter_topbar').hide();
                self.$('.o_cp_buttons').hide();
            } else if (result == 'saisie_group_partner') {
                self.$('.o_cp_sidebar').hide();
                self.$('.o_chatter_topbar').hide();
            } else if (result == 'presence_group_shift') {
                self.$('.o_cp_sidebar').hide();
                self.$('.o_chatter_topbar').hide();
                self.$('.o_cp_buttons').show();
            } else if (result == 'saisie_group_shift') {
                self.$('.o_cp_sidebar').hide();
                self.$('.o_chatter_topbar').hide();
            } else if (result == 'saisie_group_leave') {
                self.$('.o_cp_sidebar').hide();
                self.$('.o_chatter_topbar').hide();
            } else {
                self.$('.o_cp_sidebar').show();
                self.$('.o_chatter_topbar').show();
                self.$('.o_cp_buttons').show();
            }
        }

    });

    ListRenderer.include({

        _renderButton: function(record, node) {
            var self = this;
            var res = this._super.apply(this, arguments);
            if (!session.is_admin) {
                self.check_hide_buttons();
            }
            return res;
        },

        _onSelectRecord: function(event) {
            var self = this;
            this._super.apply(this, arguments);
            if (!session.is_admin) {
                self.check_hide_buttons_select()
            }
        },
        _onToggleSelection: function(event) {
            var self = this;
            this._super.apply(this, arguments);
            if (!session.is_admin) {
                self.check_hide_buttons_select()
            }
        },
        check_hide_buttons: function() {
            var self = this;
            var context = this.state.context;
            var res_model = this.state.model;
            this._rpc({
                model: 'res.users',
                method: 'check_access_buttons',
                args: [context.uid, res_model],
                context: context,
            }).then(function(result) {
                self.hide_button(result);
            });
        },

        hide_button: function(result) {
            if (result) {
                self.$('.o_button_import').hide();
            } else {
                self.$('.o_button_import').show();
            }
        },

        check_hide_buttons_select: function() {
            var self = this;
            var context = this.state.context;
            var res_model = this.state.model;
            this._rpc({
                model: 'res.users',
                method: 'check_access_buttons',
                args: [context.uid, res_model],
                context: context,
            }).then(function(result) {
                self.hide_button_select(result);
            });
        },

        hide_button_select: function(result) {
            if (result) {
                self.$('.o_cp_sidebar ').hide();
            } else {
                self.$('.o_cp_sidebar').show();
            }
        },



    })

});
