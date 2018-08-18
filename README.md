# Udacity Full-stack Nanodegree Project

## Movie Catalog

## Prerequisites

* [Vagrant](https://www.vagrantup.com/)
* [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## How to Run

* Install Vagrant and VirtualBox
* Clone the Vagrantfile from the Udacity Repo
* Clone this repo into the `catlog/` directory found in the Vagrant directory
* Run `vagrant up` to run the virtual machine, then `vagrant ssh` to login to the VM
* Initialize the database with `python database_setup.py`
* Populate the database with `python lotsofmovies.py`
* Launch application with `python project.py`
* Open the browser and go to `http://localhost:5000` to access the application

## JSON endpoints

* Returns JSON of all Genres - `/genres/JSON`
* Returns JSON of all Movies in the selected Genre - `/genres/<int:genre_id>/movies/JSON`
* Returns JSON of a selected Movie - `/genres/<int:genre_id>/movies/<int:movie_id>/JSON`
