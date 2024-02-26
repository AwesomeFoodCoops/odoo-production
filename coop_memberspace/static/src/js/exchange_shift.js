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
                                <span>${self.get_cancel_label()} </span>
                                <button class="material-icons button-icon remove-proposal"
                                    registration-id="${registration_id}"
                                    data-toggle="modal" data-target="#modal_confirm_cancel_proposal">remove_circle_outline</button>
                            `;
                            let parent = $(btn_go_to_market).parent();
                            while(parent.children(":first").length > 0) {
                                parent.children(":first").remove();
                            }
                            parent.append(data);
                            //$(btn_go_to_market).remove();
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
                $('.exchange-shift').on('click', '.browse-expected-attendee', function(e) {
                    let shift_id = parseInt($(this).attr('shift-id'));
                    self._rpc({
                        model: 'shift.shift',
                        method: 'get_expected_attendee',
                        args: [[shift_id]],
                    })
                    .then(function(partners){
                        $('.modal_list_expected_attendee_body').empty();
                        if(partners.length) {
                            partners.forEach(function(partner, idx, array) {
                                let data = `
                                    <tr>
                                        <td>${partner}</td>
                                    </tr>
                                `;
                                $('.modal_list_expected_attendee_body').append(data);
                            })
                        }
                    })
                });
                $('.exchange-shift').on('click', '.select-shift-proposal', function(e) {
                    self.shift_on_market = parseInt($(this).attr('registration-id'));
                    self.shift_available = parseInt($(this).attr('shift-id'));
                    $.blockUI();
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
                        } else if(shifts.length === 1){
                            let src_registration_id = self.shift_on_market;
                            let src_shift = self.shift_available;
                            let des_registration_id = shifts[0].id;
                            self.des_registration_id = des_registration_id;
                            let resp = self.show_shift_proposal_confirmation(src_registration_id, src_shift, des_registration_id);
                            resp.then(function(){
                                $('#modal_confirm_exchange_shift').modal('show');
                            });
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
                            $('#modal_exchange_shift').modal('show');
                        }
                    })
                    .always(function () {
                        $.unblockUI();
                    });
                });

                $('.exchange-shift').on('click', '.confirm-shift-proposal', function(e) {
                    let src_registration_id = self.shift_on_market;
                    let src_shift = self.shift_available;
                    let des_registration_id = parseInt($('input[name=registration_input]:checked').val());
                    let resp = self.show_shift_proposal_confirmation(src_registration_id, src_shift, des_registration_id);
                    resp.then(function(){
                        $('#modal_exchange_shift').modal('hide');
                    });
                });
                $('#modal_confirm_exchange_shift').on('click', '.create-proposal', function(e) {
                    let src_registration_id = self.shift_on_market;
                    let des_registration_id = parseInt($('input[name=registration_input]:checked').val());
                    if (!des_registration_id && self.des_registration_id !== undefined){
                        des_registration_id = self.des_registration_id;
                    }
                    let src_shift = self.shift_available;
                    $.blockUI();
                    self._rpc({
                        model: 'shift.registration',
                        method: 'create_proposal',
                        args: [src_registration_id, des_registration_id, src_shift],
                    })
                    .then(function(){
                        window.location.reload();
                        $('#modal_confirm_exchange_shift').modal('hide');
                    })
                    .fail(function(error, event) {
                        $.unblockUI();
                        $('#modal_confirm_exchange_shift').modal('hide');
                    })
                    .always(function () {
                        // $.unblockUI();
                    });;
                });
            },
            get_cancel_label: function () {
                return "En cours";
            },
            show_shift_proposal_confirmation: function (src_registration_id, src_shift, des_registration_id){
                return this._rpc({
                    model: 'shift.registration',
                    method: 'shifts_to_confirm',
                    args: [src_registration_id, des_registration_id, src_shift],
                })
                .then(function(resp){
                    var code = resp[0];
                    var mesg = resp[1];
                    $('.modal_confirm_shift_body').empty();
                    $('.modal_confirm_shift_body').append('<span>' + mesg + ' </span>');
                    if(!des_registration_id || code === 0) {
                        $('.create-proposal').addClass('d-none');
                    }
                    else {
                        $('.create-proposal').removeClass('d-none');
                    }
                });
            }
        })
});
