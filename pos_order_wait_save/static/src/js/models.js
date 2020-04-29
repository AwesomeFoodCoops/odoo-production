/* Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define('pos_order_wait_save.models', function (require) {
    "use strict";
    var pos_model = require('point_of_sale.models');
    var OrderSuper = pos_model.Order.prototype;
    pos_model.Order = pos_model.Order.extend({
        initialize: function (attributes, options) {
            OrderSuper.initialize.apply(this, arguments);
            this.is_not_saved_yet = false;
        },
        export_as_JSON: function () {
            var res = OrderSuper.export_as_JSON.apply(this, arguments);
            res.is_not_saved_yet = this.is_not_saved_yet;
            return res;
        },
        export_for_printing: function () {
            var res = OrderSuper.export_for_printing.apply(this, arguments);
            res.is_not_saved_yet = this.is_not_saved_yet;
            return res;
        },
    });
    pos_model.PosModel = pos_model.PosModel.extend({
        _flush_orders: function (orders, options) {
            var self = this;
            var new_timeout = self.config.order_wait_save_timeout * 1000;
            options.timeout = new_timeout;
            this.set('synch', {state: 'connecting', pending: orders.length});
            return self._save_to_server(orders, options).done(function (server_ids) {
                var pending = self.db.get_orders().length;
                self.set('synch', {
                    state: pending ? 'connecting' : 'connected',
                    pending: pending,
                });
                return server_ids;
            }).fail( function (error, event) {
                var pending = self.db.get_orders().length;
                if (self.get('failed')) {
                    self.set('synch', {state: 'error', pending: pending});
                } else {
                    self.set('synch', {state: 'disconnected', pending: pending});
                }
            });
        },
    });

});
