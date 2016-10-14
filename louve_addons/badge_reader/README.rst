.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Ionic Apps - Badge Reader
=========================

Provide light JS apps that provides badge reader interface.

Once installed, the apps is available via this url
http://localhost:8069/badge_reader/static/www/index.html (by default)

Authentication
--------------

User must select Database name, login and password. (The user must be
member of the new group 'Badge Reader - Manager')

.. image:: /badge_reader/static/description/authentication.png

User Search
-----------

User should scan User barcode.

.. image:: /badge_reader/static/description/user_search.png

If the barcode is unknown a specific sound is played.

.. image:: /badge_reader/static/description/user_not_found.png

Partner Form
------------

If the barcode matches with a user, the partner is display with some
informations.

.. image:: /badge_reader/static/description/partner_success.png


If the partner has some special state, an alternative background color is
displayed with the reason.

.. image:: /badge_reader/static/description/partner_warning.png

Move Logs
---------

The use of this badge reader is logged and and logs are available in
back-office

.. image:: /badge_reader/static/description/user_moves.png

Technical Information - Back office
-----------------------------------

* Create a new group 'Badge Reader - User' User must be member
  of that group to access to the history of the logs;

* Create a new group 'Badge Reader - Manager' User must be member
  of that group to log into the JS apps;


Technical Information - JS Apps
-------------------------------

The extra libs used are

* Bootstrap - v3.3.6 <http://getbootstrap.com>

* AngularJS - v1.3.15 <http://angularjs.org>

* IonicJS - v1.0.0 <http://ionicframework.com/>

* Angular Odoo <https://github.com/akretion/angular-odoo>, little JS framework
  based on angular, that provides functions to connect and communicate with
  Odoo / OCB


Possible Improvments
====================

* display partner with bootstrap colors in kanban and tree view

* The JS apps is not translatable for the time being and is available only
  in french

Credits
=======

Contributors
------------

* Sylvain LE GAL <https://twitter.com/legalsylvain>

Icon module comes from <https://www.iconfinder.com/icons/52644/card_reader_security_icon> and is copyright by <www.tpdkdesign.net>

