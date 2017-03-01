.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========
Coop Shift
==========

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

Configuration
=============

We define a config_parameter_weekA parameter to store the date of a Monday of
weekA (with format YYYY-MM-DD)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/shewolfParis/louve_addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Julien Weste <julien.weste@akreation.com.br>
* Sylvain LE GAL <https://twitter.com/legalsylvain>
