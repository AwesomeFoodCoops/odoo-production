odoo.define('coop_memberspace.programmer_un_service', function (require) {
    "use strict";

    var snippet_animation = require('web_editor.snippets.animation');
    var session = require('web.session');
    var Model = require('web.Model');
    var ajax = require("web.ajax");

    snippet_animation.registry.programmer_un_service =
		snippet_animation.Class.extend({
            selector: '.programmer_un_service',
            start: function () {
                var self = this;
                ajax.jsonRpc("/web/session/get_session_info", "call").then(function (sessiondata) {
                    self.session = sessiondata;
                });
                $('.fa.fa-user-plus').on('click', function() {
                    let shift_id = $(this).attr('data-shift-id');
                    self.shift_id = shift_id;
                    let shift_type = $(this).attr('data-shift-type');
                    self.shift_type = shift_type;
                    let time = $('#time-' + shift_id).text();
                    $('#modal_time').text(time);
                });

                $('.fa.fa-check').on('click', function(e) {
                    e.preventDefault();
                    let btn_check = this;
                    $(btn_check).attr("disabled", "disabled");
                    new Model('shift.ticket').call(
                        'search', [[['shift_id', '=', parseInt(self.shift_id)], ['shift_type', '=', self.shift_type]]])
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
                                $('#btn-add-' + self.shift_id).hide();
                                let no_available_seats = '#avalable-seats-' + self.shift_id;
                                $(no_available_seats).text(parseInt($(no_available_seats).text()) - 1);
                                let shift = "#shift-" + self.shift_id;
                                $(shift).css({'color': 'grey', 'background-color': '#e7e7e7'});
                                $('#programmer_modal').modal('hide');
                                $(btn_check).removeAttr("disabled");
                            })
                            .fail(function(error, event) {
                                $('#error_header').text(error.message);
                                $('#error_body').text(error.data.arguments[0] || '');
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
