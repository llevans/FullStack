README
======

Catalog CRUD project - Composer's Catalog
------------------------------------------

This application is a python webmodule used to manage a catalog of classical music composers.
The web application is available at url "http://localhost:5000/"

The application will be run on a VirtualBox VM. The virtual machine is configured through Vagrant.
Vagrant configures file system sharing between the VM and your host machine. It also configures
the HTTP request forwarding to your local host machine.

The appplication authenticates using Google+ OAuth services.

Steps:
   1.) Install the VirtualBox VM
        download and install the proper platform package for your operating system
           https://www.virtualbox.org/wiki/Downloads
        download and install Vagrant to configure the VirtualBox VM
           https://www.vagrantup.com/downloads
        copy Vagrant and PostgreSQL configuration into the created ~/vagrant directory
           cp ~/{...}/VagrantFile to ~/vagrant
           cp ~/{...}/pg_config.sh to ~/vagrant

   2.) Run the VirtualBox VM
        move to the ~/vagrant subdirectory
           'cd ~/{ .. }/vagrant'
        start the VM
           'vagrant up'
        access the VM through a secure shell
           'vagrant ssh'

   3.) Prepare the Postgres database
        After connecting to the VM ('vagrant ssh'), move to the ~/vagrant subdirectory
           'cd ~/{ .. }/vagrant'
        run python scripts to setup the composer's catalog (database)
           'python db_setup.py'
           'python db_populate.py'

   4.) Start the Composer's Catalog application 
        After connecting to the VM ('vagrant ssh'), move to the catalog project subdirectory
           'cd /vagrant/{...}/catalog'
        start the python project (Flask web server)
           'python project.py'
        open the application
           open url http://localhost:5000/ in a browser
        login to access admin functions (add, edit, delete)
           click the Google+ signin button at the application banner (login using your Google username/password)
           
   5.) Halt the VirtualBox VM
        exit the SSH session
           'exit'
        halt the VM
           'vagrant halt'


Functions are available to manage the Composers' catalog:
  1. List all Composers
        - http://localhost:5000/
  2. List Composers in a specific era 
        - http://localhost:5000/era/Classical/composers
  3. View Composer's detail 
        - http://localhost:5000/era/Classical/Wolfgang%2520Amadeus%2520Mozart
  4. Add a new Composer
        - http://localhost:5000/era/composer/new
  5. Edit Composer's name, description and era
        - http://localhost:5000/era/Contemporary/Conrad%20Tao/edit
  6. Delete a Composer
        - http://localhost:5000/era/Contemporary/Conrad%20Tao/delete


Endpoints are availble to aquire the Composers' catalog:
  1. Atom Composers List 
        - http://localhost:5000/composers.atom
  2. Json Era Full List 
        - http://localhost:5000/era/list/JSON
  3. Json Composers per Era List 
        - http://localhost:5000/era/1/list/JSON
  4. Json Composer Detail
        - http://localhost:5000/era/1/composer/7/JSON

