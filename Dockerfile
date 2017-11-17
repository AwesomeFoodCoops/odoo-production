FROM debian:jessie
MAINTAINER Anybox <pverkest@anybox.fr>

# This shouldn't be use on production, this is a sample to learn dockerfile
# Here some experimentations using docker and buildout to build odoo

# Add the Anybox PGP key to verify Debian packages.
# sometimes, the key server is too busy, you may need to wait a few minutes and try again
RUN apt-key adv --keyserver hkp://pool.sks-keyservers.net --recv-keys 0xE38CEB07

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
# TODO: wkhtmltopdf is already in openerp-server-system-build-deps test if
#       generating report is fine
# TODO: I wonder if openerp-server-system-run-deps is necessary
RUN echo "deb http://apt.anybox.fr/openerp common main" > /etc/apt/sources.list.d/anybox.list && \
    set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            ca-certificates \
            curl \
            git \
            node-less \
            node-clean-css \
            python-pyinotify \
            python-renderpm \
            python-support \
            openerp-server-system-build-deps \
            openerp-server-system-run-deps \
        && curl -o wkhtmltox.deb -SL http://nightly.odoo.com/extra/wkhtmltox-0.12.1.2_linux-jessie-amd64.deb \
        && echo '40e8b906de658a2221b15e4e8cd82565a47d7ee8 wkhtmltox.deb' | sha1sum -c - \
        && dpkg --force-depends -i wkhtmltox.deb \
        && apt-get -y install -f --no-install-recommends \
        && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false npm \
        && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

RUN adduser --home=/opt/odoo --disabled-password --gecos "" odoo

RUN mkdir /opt/odoo/odoo
ADD . /opt/odoo/odoo
RUN chown odoo:odoo -R /opt/odoo/odoo/
USER odoo
WORKDIR /opt/odoo/odoo
RUN python /opt/odoo/odoo/bootstrap.py -c /opt/odoo/odoo/buildout.cfg && \
   /opt/odoo/odoo/bin/buildout -c /opt/odoo/odoo/buildout.cfg

# Expose longpolling port as well?
EXPOSE 8069
# if we want to contribute to community addons or OCB we may want
# add some volume
# I wonder if we could save time at build time sharing eggs
VOLUME ['/opt/odoo/odoo', '/opt/odoo/odoo/personal-addons', /opt/odoo/odoo/etc/]
CMD ["bin/start_odoo"]
