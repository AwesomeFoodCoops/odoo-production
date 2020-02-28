odoo.define('coop_numerical_keyboard.numerical_keyboard', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var keyboard = require('point_of_sale.keyboard');
    var _t = core._t;

    keyboard.OnscreenKeyboardWidget.include({
        connect : function(target){
            var self = this;
            this.$target = $(target);
            var parent_ele = $(this.$target).parent();
            this.$target.focus(function(){
                if ($(parent_ele).hasClass('numeric_keyboard')){
                    $('.simple_keyboard').hide();
                    $('.numeric_keyboard').show();
                }
                else{
                    $('.keyboard_frame  .simple_keyboard').show();
                    $('.keyboard_frame  .numeric_keyboard').hide();
                }
                // Assign this target input to widget.
                self.$target = $(this);
                self.show();
             });
        },
    });
});
