odoo.define('foodcoop_memberspace.programmer_une_vacation', function (require) {
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
                    $('.body_ftop_programmer').empty();
                    new Model('res.users').call('ftop_get_shift')
                    .then(function(shifts) {
                        shifts.forEach(function(shift, idx, array) {
                            let promises = [];
                            promises.push(new Model('res.users').call('get_time_by_user_lang', [shift.date_begin, ['%A %B %d %Y', '%HH%M'], shift]))
                            promises.push(new Model('shift.ticket').call('read', [shift.shift_ticket_ids, ['seats_available']]));
                            $.when.apply($, promises).then(function() {
                                let shift = shifts.find(x => x.id === arguments[0][2]);
                                if (shift) {
                                    let sum = _.reduce(arguments[1], function(memo, num){
                                        return memo + num.seats_available;
                                    }, 0);
                                    $('.body_ftop_programmer').append(
                                        `<tr>
                                            <td scope="row" id="time-${shift.id}">${arguments[0][0]}</td>
                                            <td id="hour-${shift.id}">${arguments[0][1]}</td>
                                            <td id="avalable-seats-${shift.id}"><span>${sum}</span></td>
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
                                }
                            });
                        });
                        $('#ftop_programmer_modal').modal('show');
                    });
                });
                $('.fa.fa-check').on('click', function() {
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
                                $('#btn-add-' + self.shift_id).removeAttr("data-toggle").removeAttr("data-target").css({'color': 'red'});
                                let no_available_seats = '#avalable-seats-' + self.shift_id;
                                $(no_available_seats).text(parseInt($(no_available_seats).text()) - 1);
                                $('#programmer_modal').modal('hide');
                            })
                            .fail(function(error, event) {
                                $('#error_header').text(error.message);
                                $('#error_body').text(error.data.message);
                                $('#programmer_modal').modal('hide');
                                $('#error_modal').modal('show');
                            });
                        }
                    })
                });
            }
        })
});
