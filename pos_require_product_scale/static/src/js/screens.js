/*
  Copyright 2019 Coop IT Easy SCRLfs
    Robin Keunen <robin@coopiteasy.be>
  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define('pos_require_product_scale.screens', function (require) {
    "use strict";

    var screens = require("point_of_sale.screens");
    var core = require('web.core');
    var _t = core._t;

    screens.ActionpadWidget.include({
        renderElement: function () {
            var self = this;
            this._super();

            if (self.pos.config.require_product_scale) {
                this.$('.pay').click(function () {
                    if (self.gui.current_popup !== null){
                        return;
                    }
                    var lines = _.filter(
                        self.pos.get_order().get_orderlines(),
                        function(line) { return line.quantity === 1.0 && line.product.to_weight}
                    );
                    if (lines.length > 0) {
                        self.gui.back();
                        self.gui.show_popup(
                            'confirm',
                            {
                                'title': _t('Warning the product quantity 1kg for the products to weight with scale'),
                                'body': (
                                    _t('The product(s) may need to be weighted with scale: ')
                                    + _.map(lines, function(line) { return line.product.display_name }).join(', ')
                                    + ". "
                                    + _t('Are you sure that you want to continue the payment?')
                                ),
                                confirm: function(){
                                    self.gui.show_screen('payment');
                                },
                            },
                        );
                    }
                });
            }
        }
    });

    return screens;
});
