odoo.define('coop_memberspace.exchange_shift', function (require) {
    "use strict";

    var snippet_animation = require('web_editor.snippets.animation');
    var session = require('web.session');
    var Model = require('web.Model');
    var ajax = require("web.ajax");

    snippet_animation.registry.exchange_shift =
		snippet_animation.Class.extend({
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
                    new Model('shift.registration').call(
                        'write', [[registration_id], {'exchange_state': 'in_progress'}])
                    .then(function(e){
                        let data = `
                            <span>En cours </span>
                            <button class="material-icons button-icon remove-proposal"
                                registration-id="${registration_id}"
                                data-toggle="modal" data-target="#modal_confirm_cancel_proposal">remove_circle_outline</button>
                        `;
                        $(btn_go_to_market).parent().append(data);
                        $(btn_go_to_market).remove();
                    })
                });

                $('#modal_confirm_cancel_proposal').on('click', '.cancel-proposal', function(e) {
                    new Model('shift.registration').call(
                        'remove_shift_regis_from_market', [[self.registration_id]])
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
                    new Model('shift.registration').call(
                        'shifts_to_proposal', [[self.shift_on_market]])
                    .then(function(shifts){
                        $('.modal_exchange_shift_body').empty();
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
                    })
                });

                $('#modal_exchange_shift').on('click', '.create-proposal', function(e) {
                    let src_registration_id = self.shift_on_market;
                    let des_registration_id = parseInt($('input[name=registration_input]:checked').val());
                    new Model('shift.registration').call(
                        'create_proposal', [src_registration_id, des_registration_id])
                    .then(function(){
                        $('#modal_exchange_shift').modal('hide');
                    })
                    .fail(function(error, event) {
                        console.log(">>>>>>> Error", error.data.message);
                        $('#modal_exchange_shift').modal('hide');
                    });
                });
            }
        })
});
