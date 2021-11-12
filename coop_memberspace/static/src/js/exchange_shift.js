odoo.define('coop_memberspace.exchange_shift', function (require) {
    "use strict";

    var sAnimations = require('website.content.snippets.animation');
    var session = require('web.session');
    var ajax = require("web.ajax");
    sAnimations.registry.exchange_shift =
        sAnimations.Class.extend({
            selector: '.exchange-shift',
            start: function () {
                var self = this;
                ajax.jsonRpc("/web/session/get_session_info", "call").then(function (sessiondata) {
                    self.session = sessiondata;
                });
                $('.exchange-shift').on('click', '.remove-proposal', function(e) {
                    self.btn_remove = this;
                    self.registration_id = parseInt($(this).attr('registration-id'));
                });
                $('.exchange-shift').on('click', '.go-to-market', function(e) {
                    let btn_go_to_market = this;
                    let registration_id = parseInt($(this).attr('registration-id'));
                    self._rpc({
                        model: 'shift.registration',
                        method: 'add_shift_regis_to_market',
                        args: [[registration_id]],
                    })
                    .then(function(res){
                        if (res.code === 0){
                            alert(res.msg);
                        }
                        else {
                            let data = `
                                <span>En cours </span>
                                <button class="material-icons button-icon remove-proposal"
                                    registration-id="${registration_id}"
                                    data-toggle="modal" data-target="#modal_confirm_cancel_proposal">remove_circle_outline</button>
                            `;
                            $(btn_go_to_market).parent().append(data);
                            $(btn_go_to_market).remove();
                        }
                    })
                });

                $('#modal_confirm_cancel_proposal').on('click', '.cancel-proposal', function(e) {
                    self._rpc({
                        model: 'shift.registration',
                        method: 'remove_shift_regis_from_market',
                        args: [[self.registration_id]],
                    })
                    .then(function(e){
                        let data = `
                            <button class="material-icons button-icon go-to-market" style="margin-right: 10px;"
                                registration-id="${self.registration_id}">swap_horiz</button>
                        `;
                        let parent = $(self.btn_remove).parent();
                        while(parent.children(":first").length > 0) {
                            parent.children(":first").remove();
                        }
                        parent.append(data);
                        $('#modal_confirm_cancel_proposal').modal('hide');
                    })
                });

                $('.exchange-shift').on('click', '.select-shift-proposal', function(e) {
                    self.shift_on_market = parseInt($(this).attr('registration-id'));
                    self.shift_available = parseInt($(this).attr('shift-id'));
                    self._rpc({
                        model: 'shift.registration',
                        method: 'shifts_to_proposal',
                        args: [[self.shift_on_market]],
                    })
                    .then(function(shifts){
                        $('.modal_exchange_shift_body').empty();
                        if(!shifts.length) {
                            $('.create-proposal').addClass('d-none');
                            $('.modal_exchange_shift_body').append('<tr class="text-center"> <td>No shift available </td></tr>');
                        } else {
                            shifts.forEach(function(shift, idx, array) {
                                let data = `
                                    <tr>
                                        <td>${shift.date}</td>
                                        <td>${shift.hour}</td>
                                        <td><input name="registration_input" id="${shift.id}" type="radio" value="${shift.id}" /></td>
                                    </tr>
                                `;
                                $('.modal_exchange_shift_body').append(data);
                            })
                        }
                    })
                });

                $('#modal_exchange_shift').on('click', '.create-proposal', function(e) {
                    let src_registration_id = self.shift_on_market;
                    let des_registration_id = parseInt($('input[name=registration_input]:checked').val());
                    let src_shift = self.shift_available;
                    self._rpc({
                        model: 'shift.registration',
                        method: 'create_proposal',
                        args: [src_registration_id, des_registration_id, src_shift],
                    })
                    .then(function(){
                        window.location.reload();
                        $('#modal_exchange_shift').modal('hide');
                    })
                    .fail(function(error, event) {
                        $('#modal_exchange_shift').modal('hide');
                    });
                });
            }
        })
});
