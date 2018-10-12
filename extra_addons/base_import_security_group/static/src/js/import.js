odoo.define('web.ListImport', function (require) {
    "use strict";
    var core = require('web.core');
    var ListView = require('web.ListView');
    var Model = require('web.Model');

    ListView.prototype.defaults.import_enabled = false;
    ListView.include(/** @lends instance.web.ListView# */{

        load_list: function (data, grouped) {

            var self = this;
            var Users = new Model('res.users');

            var result = this._super.apply(this, arguments);
            Users.call('has_group', ['base_import_security_group.group_import_csv'])
            .then(function (result) {
                var import_enabled = result;
                self.options.import_enabled = import_enabled;
                if (import_enabled === false) {
                    self.$('o_list_button_import').hide();
                }
            });
            return result;
        },

        do_select: function(ids, records) {
            var self = this;
            var res = this._super(ids, records);
            self.hide_button();      
        },

        hide_button: function(){
            var Users = new Model('res.users');
            Users.call('has_group', ['base_import_security_group.group_import_csv'])
            .then(function (result) {
                var import_enabled = result;
                if (import_enabled === false) {
                    self.$(".oe_file_attachment[data-index='0'][data-section='other']").hide();
                    self.$("[data-section='export_current_view']").parent().parent().parent().hide();
                }
            });
        }
    });
});
