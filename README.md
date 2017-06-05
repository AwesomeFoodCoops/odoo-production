Odoo mutualization
============

That repository aims to handle a commom Odoo code for the food coops that take part in the mutualization (and found it).
Our code if free, so that coops don't want to fit in the previsous rules can freely fork this Github repository. However, we higly encourage then to not fork the common modules. In that case it would be very difficult for them to entrer in the mutualization in the future.

Repository organization
============
For maintenability purpose, all the coop have to use the same version of commun module. Thos modules are in odoo, extrat_addons and coop_addons folders.
In addition, each coop has a dedicated folder where she can build custom modules. Those modules don't have to make conflict with the common modules.

Changes proposal on common modules
============
The main collaboration process is quite simple. However, we have to experience it in order to imporve it :
* If someone want to change common module, make a PR against the dev branch. The repo management team will challenge it and if it's good, merge it. Do not forbid migration scripts.
* If someone want to build a custom module, make a PR against the dev branch. The repo management team will merge in whintin 2 days. You will get it on the production/9.0 branch on the next dev->9.0  merge (ask if its urgent).

For consistency reason, we prefer to ask to or dev supplier to make the modifications on common modules.

Upgrading process
============
Step A : on the DEV environnement
-------------
=> Developper for or repo and creates a branch from our 9.0 (production) branch
=> Developper commit changes on his own repo
=> Developper make a PR to the DEV branch : he adds to the description :
- a link to the ticket  (and he adds the link of the PR to the ticket)
- the module name we have to update
- the module name we have to install
He adds the PR link to the TMS ticket.

=> The repo management team checks the code, merge the PR against DEV branch and adds the modules names to install/update at the end of this file on the DEV branch : https://github.com/shewolfParis/odoo-production/blob/dev/upgrade_module_list

=> The hosting team connects on DEV environment by ssh and execute ./odoo_delivery_lastest.sh DB_NAME
If there is no DB_NAME parameter, the script creates a new db on the fly from the J-1 database backup.
The script pull the code, and install / update the modules specified.

The hosting team usualy delete the old DB to keep only one (that's simplier for testers) manually. (this task could be integrated to the delivery script in the future, after asking to the operatror)

=> The hosting team sets the ticket to "on dev" status and send a message to users to describe the changes (absicly a screenshot of the ticket list that have be solved).

Step B : on the PROD environnement
-------------
Once the test are conpleted, the repo management team merge DEV -> 9.0 (production branch). The hosting team connects on PROD environment by ssh and execute ./odoo_delivery_lastest.sh.
=> The hosting team sets the ticket to "on production" status and send a message to users to describe the changes (absicly a screenshot of the ticket list that have be solved).
=> Its it's required, the developper create a PR against OCA repo
