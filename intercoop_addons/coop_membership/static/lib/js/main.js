(function ($) {

    "use strict";

    $(".validate-option-event").hide();
    /*==================================================================
    [ Validate after type ]*/
    $('.validate-input .input100').each(function(){
        $(this).on('blur', function(){
            if(validate(this) == false){
                showValidate(this);
            }
        })    
    })

    $('.validate-input .bob')
  
  
    /*==================================================================
    [ Validate ]*/
    var input = $('.validate-input .input100');

    /** Hide validate alerter when focus input DOM **/
    $('.validate-form .input100').each(function(){
        $(this).focus(function(){
           hideValidate(this);
        });
    });

    $('input:radio[name=cooperator]').change(function() {
        if (this.value == 0) {
            $(this).parent().removeClass('alert-validate-cooperator');
        }
        else if (this.value == 1) {
            $(this).parent().addClass('alert-validate-cooperator');
        }
    });

    function validate (input) {
        if($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
            if($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
                return false;
            }
        }
        else if($(input).attr('name') == 'dob') {
            var value = $(input).val();
            var dob = moment(value, 'DD/MM/YYYY', true);
            if (!dob.isValid()){
                return false
            }
            if ((moment().year() - dob.year()) < 18){
                return false
            }
        }
        else{
            if($(input).val().trim() == ''){
                return false;
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');

    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();
        $(thisAlert).removeClass('alert-validate');
        $(thisAlert).find('.btn-hide-validate').remove();
    }

    /** Event validate when submiting form **/
    $('.validate-form').on('submit',function(){
        var check = true;
        $('input:radio[name=cooperator]:checked')
        var length_radio = $('.validate-input-option:checked').length;
        var event = $('.validate-input-option:checked').val();
        for(var i=0; i<input.length; i++) {
            if(validate(input[i]) == false){
                showValidate(input[i]);
                check=false;
            }
            else  if (length_radio== 0){
                $(".validate-option-event").show();
                check=false;
            }

        }
        // check if member is not already a cooperator
        if ($('input:radio[name=cooperator][value=1]:checked').length > 0){
            check = false
        }

        return check;
    });
    
    ///**** Decorate Datetime picker for Date Of Birth */
    $('.dob').datetimepicker({
            pickTime: false,
            useSeconds: false,
            startDate: moment({ y: 1900 }),
            endDate: moment().add(200, "y"),
            calendarWeeks: true,
            icons: {
                time: 'fa fa-clock-o',
                date: 'fa fa-calendar',
                up: 'fa fa-chevron-up',
                down: 'fa fa-chevron-down'
            },
            language : moment.locale(),
            // format : time.strftime_to_moment_format((this.type_of_date === 'datetime')? (l10n.date_format + ' ' + l10n.time_format) : l10n.date_format),
    });
    

})(jQuery);