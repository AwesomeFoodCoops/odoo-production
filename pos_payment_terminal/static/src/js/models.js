odoo.define('pos_payment_terminal.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    models.load_fields('account.journal', ['pos_terminal_payment_mode']);

    models.Paymentline = models.Paymentline.extend({
        get_automatic_payment_terminal: function() {
            if (this.cashregister.journal.pos_terminal_payment_mode == 'card' && this.pos.config.iface_payment_terminal) {
                return true;
            }
            else {
                return false;
            }
        },
        set_payment_terminal_return_message: function(message) {
            this.payment_terminal_return_message = message;
            this.trigger('change',this);
        }
    });

});


