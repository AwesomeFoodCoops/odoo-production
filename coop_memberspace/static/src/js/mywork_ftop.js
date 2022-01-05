odoo.define('coop_memberspace.mywork_ftop', function (require) {
    "use strict";
    var core = require('web.core');
    var sAnimations = require('website.content.snippets.animation');
    var Dialog = require('web.Dialog');

    var _t = core._t;

    sAnimations.registry.exchange_shift =
        sAnimations.Class.extend({
            xmlDependencies: ['/coop_memberspace/static/src/xml/mywork_ftop.xml'],
            selector: '.mywork_ftop',
            start: function () {
                var self = this;
                $('.mywork_ftop').on('click', '.cancel-ftop-shift', function(e) {
                    let btn_cancel = this;
                    let registration_id = parseInt($(this).attr('registration-id'));
                    let registration_name = $(this).attr('registration-name');
                    self._rpc({
                        model: 'shift.registration',
                        method: 'check_cancel_ftop_shift',
                        args: [[registration_id]],
                    })
                    .then(function(res){
                        if (res.code === 0){
                            alert(res.msg);
                        }
                        else {
                            //$(btn_cancel).remove();
                            this.dialog = new Dialog(self, {
                                size: 'medium',
                                title: _t("Confirmation"),
                                buttons: [
                                    {
                                        text: _t("Save"),
                                        classes: 'btn-primary',
                                        close: true,
                                        click: function () {
                                            self.do_cancel_ftop_registration(registration_id);
                                        }
                                    },{
                                        text: _t("Cancel"),
                                        close: true
                                    }
                                ],

                                $content: $(core.qweb.render('coop_memberspace.ftop_shift_cancel_confirmation',  {
                                    shift_name: registration_name,
                                    msg: res.data.msg,
                                    confirm_msg: res.data.confirm_msg,
                                    option: self,
                                }))
                            });
                            this.dialog.opened().then((function () {
                                
                            }).bind(this.dialog));
                            this.dialog.open();
                        }
                    })
                });
            },
            do_cancel_ftop_registration: function(registration_id){
                this._rpc({
                    model: 'shift.registration',
                    method: 'do_cancel_ftop_shift',
                    args: [[registration_id]],
                })
                .then(function(res){
                    window.location.reload();
                });
            },
        })
});
