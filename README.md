Overview
--------

This charm creates a local Pypi caching mirror.
Original code: https://jujucharms.com/u/chris-gondolin/pypi-mirror/trusty/1

Usage
-----

Step by step instructions on using the charm:

    juju deploy pypi-mirror
    juju deploy apache2
    juju set apache2 servername="mypypi.domain.com"
    juju set apache2 enable_modules="proxy proxy_http"
    juju set apache2 vhost_http_template=$(base64 -w0 pypi-mirror-vhost.template)

pypi-mirror-vhost.template should look something like this:

<VirtualHost *:80>
     ServerName {{ servername }}

     CustomLog /var/log/apache2/{{ servername }}-access.log combined
     ErrorLog /var/log/apache2/{{ servername }}-error.log

     ProxyRequests off
     <Proxy *>
          Order Allow,Deny
          Allow from All
     </Proxy>
     ProxyPreserveHost off

     ProxyPass         / http://{{ pypimirror }}/
     ProxyPassReverse  / http://{{ pypimirror }}/
</VirtualHost>


Configuration
-------------

Configuration is pretty minimal, as most of the hard work is done
by the web server.  Configurable options are:

mirror_user:
The user the mirror process runs as.  Defaults to "mirror"

nagios_context:
Used by the nrpe-subordinate charm

nagios_servicegroups:
Used by the nrpe-subordinate charm


Contact Information
-------------------

Author: Chris Stratford <chris.stratford@canonical.com>

Report bugs at: http://bugs.launchpad.net/charms/+source/pypi-mirror

Location: http://jujucharms.com/charms/trusty/pypi-mirror

