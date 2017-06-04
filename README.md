Odoo mutualization
============

That repository aims to handle a commom Odoo code for the food coops that take part in the mutualization (and found it).
Our code if free, so that coops don't want to fit in the previsous rules can freely fork this Github repository. However, we higly encourage then to not fork the common modules. In that case it would be very difficult for them to entrer in the mutualization in the future.

Repository organization
============
For maintenability purpose, all the coop have to use the same version of commun module. Thos modules are in odoo, extrat_addons and coop_addons folders.
In addition, each coop has a dedicated folder where she can build custom modules. Those modules don't have to make conflict with the common modules.

Changes process
============
The main collaboration process is quite simple. However, we have to experience it in order to imporve it :
* If someone want to change common module, make a PR against the dev branch. The repo management team will challenge it and if it's good, merge it. Do not forbid migration scripts.
* If someone want to build a custom module, make a PR against the dev branch. The repo management team will merge in whintin 2 days. You will get it on the production/9.0 branch on the next dev->9.0  merge (ask if its urgent).
