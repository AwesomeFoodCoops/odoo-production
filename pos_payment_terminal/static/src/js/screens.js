odoo.define('pos_payment_terminal.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');

    screens.PaymentScreenWidget.include({
        render_paymentlines : function(){
            this._super.apply(this, arguments);
            var self  = this;
            var line = this.pos.get_order().selected_paymentline;
            if(line){
                var auto = line.get_automatic_payment_terminal();
                $('.back').hide();
                if (auto) {
                    this.pos.proxy.payment_terminal_transaction_start(self, self.pos.currency.name);
                }
            }
        },
        transaction_error: function() {
            this.gui.show_popup('error',{
                'title': _t('Transaction error'),
                'body':  _t('Please, try it again.'),
                });
            return;
        },
    });
});
