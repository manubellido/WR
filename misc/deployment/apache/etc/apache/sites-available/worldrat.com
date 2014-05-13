<VirtualHost *:80>

  ServerName worldrat.com
  ServerAlias www.worldrat.com
  DocumentRoot "/var/vhosts/worldrat.com/redirect/public"
  DirectoryIndex index.htm index.html

  <Directory "/var/vhosts/worldrat.com/redirect/public">
   AllowOverride All
  </Directory>

  Errorlog /var/vhosts/worldrat.com/redirect/logs/redirect.worldrat.com-error.log
  CustomLog /var/vhosts/worldrat.com/redirect/logs/redirect.worldrat.com-access.log combined

</VirtualHost>

<VirtualHost *:80>

  ServerName mvp.worldrat.com
  DocumentRoot "/var/vhosts/worldrat.com/mvp/public"
  DirectoryIndex index.htm index.html

  <Directory "/var/vhosts/worldrat.com/mvp/public">
   AllowOverride All
  </Directory>

  Alias /media/ /var/vhosts/worldrat.com/mvp/code/media/

  <Directory /var/vhosts/worldrat.com/mvp/media>
        Order deny,allow
        Allow from all
  </Directory>

  Alias /static/ /var/vhosts/worldrat.com/mvp/code/static/

  <Directory /var/vhosts/worldrat.com/mvp/static>
        Order deny,allow
        Allow from all
  </Directory>

  <Directory /var/vhosts/worldrat.com/mvp/project>
        Order deny,allow
        Allow from all
  </Directory>

  WSGIScriptAlias / /var/vhosts/worldrat.com/mvp/code/project/worldrat-wsgi.py
  WSGIPassAuthorization On

  Errorlog /var/vhosts/worldrat.com/mvp/logs/mvp.worldrat.com-error.log
  CustomLog /var/vhosts/worldrat.com/mvp/logs/mvp.worldrat.com-access.log combined

</VirtualHost>

<VirtualHost *:80>

  ServerName dev.worldrat.com
  DocumentRoot "/var/vhosts/worldrat.com/worldrat/public"
  DirectoryIndex index.htm index.html

  <Directory "/var/vhosts/worldrat.com/worldrat/public">
   AllowOverride All
  </Directory>

  Alias /media/ /var/vhosts/worldrat.com/worldrat/code/media/

  <Directory /var/vhosts/worldrat.com/worldrat/media>
        Order deny,allow
        Allow from all
  </Directory>

  Alias /static/ /var/vhosts/worldrat.com/worldrat/code/static/

  <Directory /var/vhosts/worldrat.com/worldrat/static>
        Order deny,allow
        Allow from all
  </Directory>

  <Directory /var/vhosts/worldrat.com/worldrat/project>
        Order deny,allow
        Allow from all
  </Directory>

  WSGIScriptAlias / /var/vhosts/worldrat.com/worldrat/code/project/worldrat_wsgi.py
  WSGIPassAuthorization On

  Errorlog /var/vhosts/worldrat.com/worldrat/logs/dev.worldrat.com-error.log
  CustomLog /var/vhosts/worldrat.com/worldrat/logs/dev.worldrat.com-access.log combined

</VirtualHost>

<VirtualHost *:80>

  ServerName redirector.worldrat.com
  DocumentRoot "/var/vhosts/worldrat.com/redirector/public"
  DirectoryIndex index.htm index.html

  <Directory /var/vhosts/worldrat.com/redirector/code>
        Order deny,allow
        Allow from all
  </Directory>

  WSGIScriptAlias / /var/vhosts/worldrat.com/redirector/code/redirector_wsgi.py
  WSGIPassAuthorization On

  Errorlog /var/vhosts/worldrat.com/redirector/logs/redirector.worldrat.com-error.log
  CustomLog /var/vhosts/worldrat.com/redirector/logs/redirector.worldrat.com-access.log combined

</VirtualHost>
