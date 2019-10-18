odoo.define('user_menu_chouette.support_chouette', function (require) {
"use strict";

var Model = require('web.Model');
var UserMenu = require('web.UserMenu');

// Modify behaviour of addons/web/static/src/js/widgets/user_menu.js
UserMenu.include({
    on_menu_support_chouette: function () {
        var support_window = window.open('', '_blank');
        new Model('ir.config_parameter')
            .call('get_param', ['x_user_menu_support_url'])
            .then(function(url) {
                if (url) { 
                    support_window.location = url;
                }
            });
    }
});

});
