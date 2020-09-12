odoo.define('coop_memberspace.programmer_une_vacation', function (require) {
    "use strict";

    var snippet_animation = require('web_editor.snippets.animation');
    var session = require('web.session');
    var Model = require('web.Model');
    var ajax = require("web.ajax");

    snippet_animation.registry.programmer_une_vacation =
		snippet_animation.Class.extend({
            selector: '.programmer_une_vacation',
            start: function () {
                var self = this;
                ajax.jsonRpc("/web/session/get_session_info", "call").then(function (sessiondata) {
                    self.session = sessiondata;
                });
                $('.toggle-ftop-programmer').on('click', function() {
                    var button_modal = this;
                    $(button_modal).prop('disabled', true);
                    $('.ftop-programmer-text').addClass("hide");
                    $('.toggle-ftop-spinner-icon').removeClass("hide");
                    $('.toggle-ftop-spinner-text').removeClass("hide");
                    $('.body_ftop_programmer').empty();
                    new Model('res.users').call('ftop_get_shift').then(function(shifts) {
                        shifts.forEach(function(shift, idx, array) {
                            var week_number = shift.week_number;
                            var week_name = shift.week_name;
                            $('.body_ftop_programmer').append(
                                `<tr>
                                    <td scope="row">
                                        <span id="time-${shift.id}">${shift.date_begin[0] + ' '}</span>
                                        <span>${shift.date_begin[1]}</span>
                                    </td>
                                    <td t-attf-id="week-${shift.id}">
                                        ${week_name || ''}
                                    </td>
                                    <td id="hour-${shift.id}">${shift.date_begin[1]}</td>
                                    <td id="avalable-seats-${shift.id}"><span>${shift.seats_avail}</span></td>
                                    <td><a><span class="fa fa-user-plus" data-toggle="modal" data-target="#programmer_modal" id="btn-add-${shift.id}" shift-id="${shift.id}" /></a></td>
                                </tr>`
                            );
                            $('.fa.fa-user-plus').on('click', function() {
                                let shift_id = $(this).attr('shift-id');
                                self.shift_id = shift_id;
                                let time = $('#time-' + shift_id).text();
                                let hour = $('#hour-' + shift_id).text();
                                $('#modal_time').text(time);
                                $('#modal_hour').text(hour);
                            });
                        });
                        $('#ftop_programmer_modal').modal('show');
                        $('.ftop-programmer-text').removeClass("hide");
                        $('.toggle-ftop-spinner-icon').addClass("hide");
                        $('.toggle-ftop-spinner-text').addClass("hide");
                        $(button_modal).prop('disabled', false);
                    });
                });
                $('.fa.fa-check').on('click', function(e) {
                    e.preventDefault();
                    let btn_check = this;
                    $(btn_check).attr("disabled", "disabled");
                    new Model('shift.ticket').call(
                        'search', [[['shift_id', '=', parseInt(self.shift_id)], ['shift_type', '=', 'ftop']]])
                    .then(function(data) {
                        if (data.length > 0) {
                            let vals = {
                                'state': 'draft',
                                'partner_id': parseInt(self.session.partner_id),
                                'shift_id': parseInt(self.shift_id),
                                'shift_ticket_id': parseInt(data[0]),
                                'related_extension_id': false
                            }
                            new Model('shift.registration').call(
                                'create', [vals])
                            .then(function(result) {
                                new Model('shift.registration').call(
                                    'get_coordinators', [result, true])
                                .then(function(coordinators) {
                                    let time = $('#time-' + self.shift_id).text();
                                    let hour = $('#hour-' + self.shift_id).text();
                                    let new_shift = `
                                        <tr>
                                            <td scope="row">${time + ' '} ${hour}</td>
                                            <td>${hour}</td>
                                            <td><span><span>${coordinators[0] + ' '}</span> <i data-toggle="tooltip" data-container="body" title="Vous pouvez contacter vos coordinateurs en écrivant à
                                                ${coordinators[1] + ' '} (cliquez pour copier l’adresse)" class="fa fa-question-circle js-copy" data-copy="${coordinators[1]}"></i></span></td>
                                            <td><a><button type="button" style="border: 0px; background-color: transparent" class="fa fa-times" data-toggle="modal" data-target="#not_cancel_registration_modal"/></a></td>
                                        </tr>
                                    `;
                                    $('.ftop-programmer-une-vacation-body').append(new_shift);
                                    $('[data-toggle="tooltip"]').tooltip();
                                    $('.js-copy').click(function() {
                                        var text = $(this).attr('data-copy');
                                        var el = $(this);
                                        copyToClipboard(text, el);
                                    });
                                });

                                $('#btn-add-' + self.shift_id).removeAttr("data-toggle").removeAttr("data-target").css({'color': 'grey'});
                                let no_available_seats = '#avalable-seats-' + self.shift_id;
                                $(no_available_seats).text(parseInt($(no_available_seats).text()) - 1);
                                $('#programmer_modal').modal('hide');
                                $(btn_check).removeAttr("disabled");
                            })
                            .fail(function(error, event) {
                                $('#error_header').text(error.message);
                                $('#error_body').text(error.data.message);
                                $('#programmer_modal').modal('hide');
                                $('#error_modal').modal('show');
                                $(btn_check).removeAttr("disabled");
                            });
                        }
                        else {
                            $(btn_check).removeAttr("disabled");
                        }
                    })
                });
            }
        })
});
