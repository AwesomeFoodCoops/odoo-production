odoo.define('coop_memberspace_cancelation.exchange_shift', function (require) {
    "use strict";

    var sAnimations = require('website.content.snippets.animation');

    sAnimations.registry.exchange_shift.include({
        start: function () {
            this._super();
            var self = this;
            $('.exchange-shift').on('click', '.confirm-cancel-registration', function(e) {
                self.registration_id = parseInt($(this).attr('registration-id'));
                let registration_name = $(this).attr('registration-name');
                let $popup = $($(this).attr('data-target'));
                if($popup.length && $popup.find('.service_name')) {
                    $popup.find('.service_name').text(registration_name);
                }
            });
            $('.modal_confirm_cancel_registration').on('click', '.cancel-registration', function(e) {
                $(this).on("click",function(){return false;});
                self._rpc({
                    model: 'shift.registration',
                    method: 'cancel_shift_regis_from_market',
                    args: [[self.registration_id]],
                })
                .then(function(result){
                    window.location.reload();
                })
            });
        },
    })
});
