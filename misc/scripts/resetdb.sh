dropdb worldrat
createdb worldrat
psql -d worldrat -f /usr/local/share/postgis/postgis.sql
psql -d worldrat -f /usr/local/share/postgis/spatial_ref_sys.sql
# psql -d worldrat -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
# psql -d worldrat -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql
python project/manage.py syncdb
python project/manage.py migrate topics
python project/manage.py migrate googlemaps_localities
python project/manage.py migrate places
python project/manage.py migrate
psql -d worldrat -c "INSERT INTO django_site (domain, name) VALUES ('localhost', 'localhost');"
