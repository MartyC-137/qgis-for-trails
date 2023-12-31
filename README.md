# QGIS for Trail Building

<div style="display: flex; justify-content: space-between;">
    <img src="assets/pyqgis_logo.png" alt="PyQGIS" width="250" height="100">
    <img src="assets/docker.jpg" alt="Docker" width="100" height="100">
    <img src="assets/postgres.png" alt="Postgres" width="100" height="100">
</div>

## Table of Contents

- [QGIS for Trail Building](#qgis-for-trail-building)
  - [Table of Contents](#table-of-contents)
    - [Introduction](#introduction)
    - [Getting Started](#getting-started)
    - [PostGIS Setup](#postgis-setup)
    - [Setting Up The Database](#setting-up-the-database)
    - [Trail Processing Script](#trail-processing-script)

### Introduction

This repo contains a QGIS Python script for creating many useful layers for trail building.
It also includes my contour style file, and a Docker configuration to run PostgreSQL, PostGIS (Postgres support for geospatial data)
and PGAdmin on the `arm64` architecture. This will allow you to create a PostgreSQL spatial database on a Silicon Mac and manage it with PGAdmin.

This project uses the following Docker base images:

- [imresamu/postgis](https://hub.docker.com/r/imresamu/postgis) - PostGIS + PostgreSQL
- [dpage/pgadmin4](https://hub.docker.com/r/dpage/pgadmin4) - PGAdmin

### Getting Started

- [x] **Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)**

- [x] **Download [QGIS](https://www.qgis.org/en/site/forusers/download.html)**

- [x] Clone the repo:

``` sh
# Standard:
cd repo/path/here
git clone https://github.com/MartyC-137/qgis-for-trails.git

# GitHub CLI:
cd repo/path/here
gh repo clone MartyC-137/qgis-for-trails
```

### PostGIS Setup

- Create two directories in the root of the repo called `data` and `pgadmin`:

``` sh
cd postgis-docker
mkdir data pgadmin
```

- Create a file called `pgadmin_pwd.txt` containing your PG Admin password:

``` sh
echo "my_pgadmin_password" > pgadmin_pwd.txt
```

- Create a file called `postgres_pwd.txt` containing the password for connecting to and admistering the Postgis database.
Note this file is only read when initializing the Postgres database the first time the container is started with an empty data sub-directory.
If you want to change the database password after the initial container build, it will require using the `ALTER USER` command in the psql shell.

``` sh
echo "my_postgres_password" > postgres_pwd.txt
```

- If you didn't clone the repo and are working on your own, run the following:
  
``` sh
echo "*_pwd.txt" >> .gitignore
echo "data/" >> .gitignore
```

The containers are now ready to start.

### Setting Up The Database

Run the following command in a terminal:

``` sh
docker compose up --no-start
docker compose start
```

- Open a web browser and navigate to `http://localhost:5050/browser/` to start PGAdmin
- Enter your PGAdmin email/username (default: <pgadmin@pgadmin.org>) and password (your password from `pgadmin_pwd.txt`)
- Create a server named `postgis`:

![PGAdmin1](/assets/pgadmin1.jpg)

On the Connection tab, enter the following info and click Save:

- `Host name/address`: postgis
- `Port`: 5432
- `Maintenance database`: postgres
- `Username`: postgres
- `Password`: the password from `postgres_pwd.txt`

![!PGAdmin2](/assets/pgadmin2.jpg)

---

### Trail Processing Script

The python file `TrailProcessing.py` is a QGIS processing tool that creates the following:

- [x] 10 meter contours
- [x] 5 meter contours
- [x] 2 meter contours
- [x] Hillshade
- [x] Slope
- [x] Relief
- [x] Ruggedness
- [x] Aspect
- [x] Polygons of Black Diamond Terrain (Slope = 15-30&deg;)

Additionally, the script provides the option to save the vector layers to a PostGIS database w/ a spatial index:

![!QGIS Generate Trail Layers](/assets/qgis_ui.jpg)

`Database` and `Schema` are optional arguments - if no PostGIS connection is set up, the script will skip loading the created vector layers to a database.
