This module copys the event.event object to create a shift.shift object. This
will be used to define the working periods of the members of the LaLouve
cooperative, and other ones of the same type.
It also creates a shift.template object to help generating recurent shifts.

On Partners, it creates a new state 'working_state' with the following value:
* 'up_to_date': 


        ('exempted', 'Exempted'),
        ('up_to_date', 'Up to date'),
        ('alert', 'Alert'),
        ('suspended', 'Suspended'),
        ('delay', 'Delay'),
        ('blocked', 'Blocked'),
