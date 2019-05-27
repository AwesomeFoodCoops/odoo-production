<a href="https://translate.druidoo.io/engage/awesomefoodcoops/?utm_source=widget">
<img src="https://translate.druidoo.io/widgets/awesomefoodcoops/-/svg-badge.svg" alt="Estado de la traducción" />
</a>

Odoo mutualization
============

This repository aims to handle a commom Odoo source code for the food co-ops that take part in the mutualization (and found it).
Our code if free, so that co-ops don't want to fit in the previsous rules can freely fork this Github repository. However, we higly encourage then to not fork the common modules. In that case it would be very difficult for them to entrer in the mutualization in the future.

Repository organization
============
For maintenability purpose, all the co-ops have to use the same version of commun module. Those modules are in odoo, extra_addons and coop_addons folders.
In addition, each co-op has a dedicated folder where it can build custom modules. Those modules should not conflict with the common modules.

Changes proposal on common modules
============
The main collaboration process is quite simple. However, we have to experience it in order to improve it :
* If someone wants to change common module, make a PR against the dev branch. The repo management team will challenge it and if it's good, merge it. Do not forget migration scripts.
* If someone wants to build a custom module, make a PR against the dev branch. The repo management team will merge in whintin 2 days. You will get it on the production/9.0 branch on the next dev->9.0  merge (ask if its urgent).

For consistency reason, we prefer to ask to our development provider to make changes on common modules.

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

=> The repo management team checks the code, and merge the PR against DEV branch

=> The hosting team update the code on staging instance, restore the lastest nighly DB copy, install/uninstall/update module dans execute migration scripts. They set the ticket to "on dev" status and send a message to users to describe the changes (basicly a screenshot of the ticket list that have be solved).

Step B : on the PROD environnement
-------------
Once the test are conpleted, the repo management team merge DEV -> 9.0 (production branch). 

=> The hosting team update the code on staging instance, install/uninstall/update module dans execute migration scripts. They set the ticket to "on prod" status and send a message to users to describe the changes (basicly a screenshot of the ticket list that have be solved).

=> If the module is generic (inside the OCA repository), the developper create a PR against OCA repo
