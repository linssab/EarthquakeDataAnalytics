# Earthquake Monitor Server and Aplication

<p>
<a href=https://img.shields.io/badge/requires-Docker-blue alt="Docker">
<img src="https://img.shields.io/badge/requires-Docker-blue" /></a>
</p>

This is an application to monitor earthquake events using the USGS API.
The data is fetched with either the Python application or with the [Apache NiFi][Apache NiFi] framework. 
The information is persistently stored in a local [Oracle database][Oracle database] running in a Docker container.

<p style="align:center; margin:auto; width:75%">
	<img src="https://i.ibb.co/hgQFtkn/mapa.png" alt="screenshot" border="0">
</p>

The [Apache NiFi][Apache NiFi] framework is also containerized, using another Docker image 
([HortonWorks Data Flow sandbox] -- check for CDF deployment in the link).

>**NOTE**: To set up the NiFi server, you will need a machine with **AT LEAST** 32Gb of RAM, 
The NiFi framework makes the ingestion of data easier and more robust. 
If you want to run the application without the NiFi server just change the 
`NIFI` variable in `./shared/EnvironmentVariables.py` file to `False`

The NiFi **server** is responsible for collecting data 
from USGS via REST queries and digesting that information into our [Oracle database][Oracle database] constantly,
independetly of the Python application, which in this case runs as a _shell_ to access our database.
<ins>Without NiFi, data is only collected when the Python application is running.</ins>

<p style="align:center; margin:auto; width:85%">
	<img src="https://i.ibb.co/phVFJJD/ss1.png" alt="screenshot" border="0">
</p>

In the next steps you will find out how to set up the **Python application**, the **database** and the **NiFi framework**.
___

## Setting up the Python Aplication

The first thing we need to do is clone this repository or download the source code and
extract it somewhere.

To clone it, use the following command:
```console
git clone https://github.com/linssab/EarthquakeDataAnalytics
```


It is strongly recommended to create a separate Python environment now.

In the new environment (or in your default Python installation) install all the required Python packages 
using the `requirements.txt` file:

```console
pip install -r requirements.txt
```

### EnvironmentVariables.py

In the [Environment Variables][envinronmentVariables] file you need to set some parameters.
To properly access our database, which we will create in the next steps, we must give our program a way to
communicate with it. 

Download the [OracleClient][OracleClient] and **extract** it somewhere in your hard drive. Next, replace the
value of the `ORACLE_CLIENT_PATH` variable in the [Environment Variables][envinronmentVariables] to math the path
where you have extracted the [OracleClient][OracleClient].

If you are not using the Apache NiFi Framework, set the `NIFI` variable to False.
The `REFRESH_RATE_NO_NIFI` variable sets the frequency with which the Python application requests data from
the USGS API. The default value is `600` seconds.
___

## Setting up the Oracle Database

We will be running our server with *containers*, so the first thing you must do is **install [Docker][Docker] 
in your machine.** Just follow the installation steps reported in the link. 

Afterwards, run the shell script for your system, as explained below:

___
### WINDOWS
Once properly installed, you must run the [databaseSetup.ps1][ps1] script from the application level, _i.e._ 
open the terminal in the folder where you have cloned the repository and execute the following commands:

```PowerShell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted -Force;
```

```PowerShell
.\databaseSetup.ps1
```
___
### UNIX
Run the [databaseSetup.sh][shell] shell script to setup the database. The script must be run from the applicaiton 
level, _i.e._  open the terminal in the folder where you have cloned the repository and execute the following command:
```shell
bash databaseSetup.sh
```
___
The script will take care of downloading the docker image and setting up the database for use.
Once it is finished, the container will be running.
___

## Configuring the Apache NiFi server

The deployment of the server is pretty simple. Download the latest scripts from Cloudera [here][CDFscripts] and extract them.

Next, open the terminal (if you are on a **Windows** machine you will need the download the [Git Bash][GitBash] first).
Open the bash terminal and execute the deploy shell script.

```console
cd /path/to/script
sh docker-deploy-{HDFversion}.sh
```

For more details refer to the [Cloudera tutorial][HortonWorks Data Flow sandbox].

After the HDF docker image is running (it may take a while to start all services), we must open our NiFi canvas.
To do so, head over to <a href=http://localhost:1080>http://localhost:1080</a> and click on the NiFi UI.

Once in the canvas, you can **import** the *.xml template provided in the [flow][flow] directory by using the import 
template button on the upper-left portion of the NiFi canvas. Once done, start all processors and the server 
will start collecting data from that moment onwards.

To shut down the server, use the following commands one after the other:

```console
docker stop sandbox-hdf
docker stop sandbox-proxy
```

Analogously, to start them again, use the following commands:
```console
docker start sandbox-hdf
docker start sandbox-proxy
```

You no longer need to run the deploy scripts after the first time.


[OracleCLient]: https://download.oracle.com/otn_software/nt/instantclient/213000/instantclient-basiclite-windows.x64-21.3.0.0.0.zip
[Apache NiFi]: https://nifi.apache.org/
[Oracle database]: https://hub.docker.com/r/gvenzl/oracle-xe
[HortonWorks Data Flow sandbox]: https://www.cloudera.com/tutorials/sandbox-deployment-and-install-guide/3.html
[Docker]: https://docs.docker.com/get-docker/
[Oracle SQL Developer]: https://www.oracle.com/tools/downloads/sqldev-downloads.html
[sqls]: https://github.com/linssab/EarthquakeDataAnalytics/tree/master/sqls
[ps1]: https://github.com/linssab/EarthquakeDataAnalytics/tree/master/databaseSetup.ps1
[shell]: https://github.com/linssab/EarthquakeDataAnalytics/tree/master/databaseSetup.sh
[envinronmentVariables]: https://github.com/linssab/EarthquakeDataAnalytics/tree/master/shared/EnvironmentVariables.py
[CDFScripts]: https://www.cloudera.com/downloads/hortonworks-sandbox/hdf.html?utm_source=mktg-tutorial
[GitBash]: https://gitforwindows.org/
[flow]: https://github.com/linssab/EarthquakeDataAnalytics/tree/master/flow