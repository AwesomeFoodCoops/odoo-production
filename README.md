[![Build Status](https://travis-ci.org/AwesomeFoodCoops/odoo-production.svg?branch=9.0)](
https://travis-ci.org/AwesomeFoodCoops/odoo-production)

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


Create your development platform
============

You want to hack a bit on your laptop! Here some tips to create a development
platform and reproduce production platform. To reproduce that environement
we are using [anybox.recipe.odoo][aro] (a [buildout][buildout] recipe),

Quick start using buildout on debian laptop assuming you already get
[dependencies][aro_dependencies]:

    # Cloning this repo
    git clone git@github.com:AwesomeFoodcoops/odoo-production.git
    cd odoo-production
    # work on a new branch based on 9.0 branch
    git clone origin/9.0 -b my_new_feature
    # bootstrap buildout (to install buildout itself)
    ~/path-to-venv-py2.7/bin/python bootstrap.py -c buildout.cfg
    # running buildout to get all requirments needs by your odoo instance
    bin/buildout -c buildout_<coop_name>.cfg
    # creating a test db with demo data to run unitest
    createdb mydbtest
    bin/upgrade_<coop name> --init-load-demo-data
    # running tests
    bin/nosetests -d mydbtest -- -s -v louve_addons/ extra_addons/
    # run odoo to test the UI and open your browser on http://localhost:8069
    bin/start_odoo -d mydbtest

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

[aro]: http://docs.anybox.fr/anybox.recipe.odoo/current
[buildout]: http://www.buildout.org/en/latest
[aro_dependencies]: http://docs.anybox.fr/anybox.recipe.odoo/current/first_steps.html#installing-build-dependencies
