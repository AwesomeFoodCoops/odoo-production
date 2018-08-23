odoo.define('coop_memberspace.my_profile', function (require) {
    "use strict";

    var snippet_animation = require('web_editor.snippets.animation');
    var session = require('web.session');
    var Model = require('web.Model');
    var ajax = require("web.ajax");

    snippet_animation.registry.my_profile =
		snippet_animation.Class.extend({
            selector: '.my_profile',
            start: function () {
                var self = this;
                ajax.jsonRpc("/web/session/get_session_info", "call").then(function (sessiondata) {
                    self.session = sessiondata;
                });

                // Edit Phone number
                $('.btn-edit-phone').on('click', function(){
                    $('input[name=mobile]').removeAttr("disabled").removeClass('input-no-edit');
                    $('input[name=phone]').removeAttr("disabled").removeClass('input-no-edit');
                    $(this).addClass("hide");
                    $(this).parent().append(
                        `<div class="row">
                            <div class="col-xs-6 col-sm-6 col-md-6 pd-l-20 pd-r-20">
                                <button type="button" class="btn btn-default btn-cancel-edit-phone">Annuler</button>
                            </div>
                            <div class="col-xs-6 col-sm-6 col-md-6 pd-l-20 pd-r-20">
                                <button class="btn btn-primary">Soumettre</button>
                            </div>
                        </div>`
                    );

                    $('.btn-cancel-edit-phone').on('click', function(){
                        $('input[name=mobile]').attr("disabled", true).addClass('input-no-edit');;
                        $('input[name=phone]').attr("disabled", true).addClass('input-no-edit');
                        $('.btn-edit-phone').removeClass('hide');
                        $(this).parents().eq(1).remove();
                    });
                });

                // Edit address
                $('.btn-edit-address').on('click', function(){
                    $('.address-no-edit').addClass('hide');
                    $('.address-edit').removeClass('hide');
                    $(this).addClass("hide");
                    $(this).parent().append(
                        `<div class="row"><div class="col-xs-6 col-sm-6 col-md-6 pd-l-20 pd-r-20">
                            <button type="button" class="btn btn-default btn-cancel-edit-address">Annuler</button>
                        </div>
                        <div class="col-xs-6 col-sm-6 col-md-6 pd-l-20 pd-r-20">
                            <button class="btn btn-primary">Soumettre</button>
                        </div></div>`
                    );
                    $('.btn-cancel-edit-address').on('click', function(){
                        $('.address-no-edit').removeClass('hide');
                        $('.address-edit').addClass('hide');
                        $('.btn-edit-address').removeClass('hide');
                        $(this).parents().eq(1).remove();
                    });
                });

                // Public avatar, email, mobile
                $('input[name=public_avatar]').change(function(){
                    if($(this).prop('checked')) {
                        new Model('res.partner').call(
                            'write', [[self.session.partner_id], {'public_avatar': true}]
                        )
                    } else {
                        new Model('res.partner').call(
                            'write', [[self.session.partner_id], {'public_avatar': false}]
                        )
                    }
                });

                $('input[name=public_mobile]').change(function(){
                    if($(this).prop('checked')) {
                        new Model('res.partner').call(
                            'write', [[self.session.partner_id], {'public_mobile': true}]
                        )
                    } else {
                        new Model('res.partner').call(
                            'write', [[self.session.partner_id], {'public_mobile': false}]
                        )
                    }
                });

                $('input[name=public_email]').change(function(){
                    if($(this).prop('checked')) {
                        new Model('res.partner').call(
                            'write', [[self.session.partner_id], {'public_email': true}]
                        )
                    } else {
                        new Model('res.partner').call(
                            'write', [[self.session.partner_id], {'public_email': false}]
                        )
                    }
                });
            }
        })
});
