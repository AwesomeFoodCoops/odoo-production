/*
License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/


odoo.define('pos_order_line_removal.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var _t = core._t;

    screens.OrderWidget.include({
        set_value: function(val) {
            var order = this.pos.get_order();
            var selectedLine = order.get_selected_orderline();
            if (this.pos.config.pos_line_remove_warning && val == 'remove' && selectedLine) {
                const self = this;
                const super_func = self._super;
                const super_arguments = arguments;
                this.gui.show_popup('confirm', {
                    'title': _t('Confirming'),
                    'body': _t('You are about to remove the item') + 
                        ' ' + selectedLine.product.display_name + ' ' +
                        _t('from the receipt. Please confirm or cancel'),
                    confirm: function () {
                        super_func.apply(self, super_arguments);
                    },
                });
            }
            else {
                this._super(val);
            }
        },
        render_orderline: function () {
            var node = this._super.apply(this, arguments);
            var self = this;

            $(node).find('.remove-line-button').on('click', null,
                this.remove_line.bind(self));

            return node;
        },
        remove_line: function (ev) {
            var orderline = ev.delegateTarget.parentElement.orderline;
            if (this.pos.config.pos_line_remove_warning && orderline) {
                this.gui.show_popup('confirm', {
                    'title': _t('Confirming'),
                    'body': _t('You are about to remove the item') + 
                        ' ' + orderline.product.display_name + ' ' +
                        _t('from the receipt. Please confirm or cancel'),
                    confirm: function () {
                        orderline.set_quantity('remove');
                    },
                });
            }
            else {
                orderline.set_quantity('remove');
            }
        },
    });
});