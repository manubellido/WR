Installation Instructions
=========================

Dependencies:

+ python 2.7
+ git
+ postgresql 8.4+
+ postgis 1.5
+ ImageMagick 6.6.0+ or graphicsmagick
+ sorl

Clone project from github
-------------------------

	git clone git@github.com:worldrat/worldrat.git

If you are reading this chances are you already did.

Install a VirtualEnv environment
--------------------------------

	cd worldrat
	virtualenv env
	source env/bin/activate

Install Python dependencies using pip
-------------------------------------

	env/bin/pip install --upgrade -r REQUIREMENTS.txt

After that we need to install GeoIP by hand. While inside the virtual env execute:
    wget http://www.maxmind.com/download/geoip/api/python/GeoIP-Python-1.2.7.tar.gz
    tar -xvzf GeoIP-Python-1.2.7.tar.gz
    cd GeoIP-Python-1.2.7/
    python setup.py build
    python setup.py install

After that you can do rm GeoIP-Python-1.2.7.tar.gz && rm -vR GeoIP-Python-1.2.7/

On OS X you can install these requirements using MacPorts like this:

sudo port install libgeoip GeoLiteCity

==> NOTE FOR MAC OS X USERS USING MACPORTS <==

If you find errors building the psycopg2 mentioning the "_PQBackendPID" symbol, a possible solution is to download the source of the this Python module by had, unpack it and then edit the setup.cfg file making the 
"pg_config" entry to point to the correct location of the binary in your system.

For PostgreSQL 8.4 installed via MacPorts, the path is:
`/opt/local/lib/postgresql84/bin/pg_config`

    wget -c http://www.initd.org/pub/software/psycopg/psycopg2-latest.tar.gz
    tar zxpf psycopg2-latest.tar.gz
    cd psycopg2-2.4/
    vim setup.cfg
    .../env/python setup.py install

Setting up the database
-----------------------

First we create the postgis template

      POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/postgis-1.5
      createdb -E UTF8 template_postgis
      createlang -d template_postgis plpgsql # Adding PLPGSQL language support.
      # Allows non-superusers the ability to create from this template
      psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
      # Loading the PostGIS SQL routines
      psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql
      psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
      Enabling users to alter spatial tables.
      psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
      psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
      psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
      createuser -P worldrat

Finally run syncdb

     env/bin/python project/manage.py syncdb
     env/bin/python project/manage.py migrate

When prompted for user create answer like this:

    Shall the new role be a superuser? (y/n) n
    Shall the new role be allowed to create databases? (y/n) n
    Shall the new role be allowed to create more new roles? (y/n) n

See [this link](https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#post-installation) for more information.


Configuring Celery Broker with Supervisor
-----------------------------------------

    apt-get install supervisor

and then copy this script into /etc/supervisor/conf.d/django-celery.conf

    ````
    ; =======================================
    ;  celeryd supervisor example for Django
    ; =======================================

    [program:celery]
    command=/var/vhosts/worldrat.com/worldrat/dev/env/bin/python /var/vhosts/worldrat.com/worldrat/dev/project/manage.py celeryd --loglevel=INFO
    directory=/var/vhosts/worldrat.com/worldrat/dev/project
    user=nobody
    numprocs=1
    stdout_logfile=/var/log/celeryd.log
    stderr_logfile=/var/log/celeryd.log
    autostart=true
    autorestart=true
    startsecs=10

    ; Need to wait for currently executing tasks to finish at shutdown.
    ; Increase this if you have very long running tasks.
    stopwaitsecs = 600

    ; if rabbitmq is supervised, set its priority higher
    ; so it starts first
    priority=998
    ````


Running the Test Envioroment
----------------------------

Run server, run:

    env/bin/python project/manage.py runserver 0.0.0.0:8000 --settings=settings


## Additional notes

### Installing PostGIS 1.5.x on Ubuntu 10.04

    sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
    sudo apt-get install postgis=1.5.2-2~lucid1
    sudo apt-get install postgresql-8.4-postgis=1.5.2-2~lucid1

### Installing PostGIS 1.5.x on Ubuntu 12.04

sudo apt-get install postgresql postgresql-client libpq-dev postgis postgresql-9.1-postgis

### Installing packages for GeoIP Database

    # donwload geoip c library and install
    http://www.maxmind.com/download/geoip/api/c/
    # install as following
    sudo ./configure
    sudo make
    sudo make check
    sudo make install
    
    # download geoip-python
    http://www.maxmind.com/download/geoip/api/python/
    # install as following
    python2 setup.py build
    python2 setup.py install


--------
(c) 2012 - Landmarker S.A.C. - All rights reserved
