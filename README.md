# Earthquake Monitor Server and Aplication

This is an application to monitor earthquake events using USGS data.
To set up the server, you will need a machine with **AT LEAST** 32Gb of RAM.
The **server** is responsible for collecting data from USGS via REST queries and digesting that information into our [Oracle database][Oracle database].

The server runs with the [Apache NiFi][Apache NiFi] framework using the [HortonWorks Data Flow sandbox] (check for CDF deployment in the link).

In the next steps you will find out how to set up the server.
___

## Setting up the Oracle Database

We will be running our server with *containers*, so the first thing you must do is install [Docker][Docker] in your machine.
You will find the installation steps in the link.

With Docker installed, you will need to pull the database image with the following command:
```console
docker pull gvenzl/oracle-xe
```

Then, to **RUN** our database container, use the following command: (insert a password you won't forget!)
```console
docker run -d -p 1521:1521 -e ORACLE_PASSWORD=<your password> -v oracle-volume:/opt/oracle/oradata gvenzl/oracle-xe --name OracleXE
```
This will run a container in detached mode mapping the port 1521 (from where we will access our database)
You will **NEVER** need to run this command again. Whenever you want to drop the container or restart it, you will use the commands

```console
docker stop OracleXE
``` 

and 

```console
docker start OracleXE
```
___

### Accessing our database for the first time

To access the database, we need another program: [Oracle SQL Developer][Oracle SQL Developer].

You can download it from the link above. Oracle MAY require you to create an account for that.
Just download the proper version for your system and unzip the files somewhere.

When you run the SQL Developer, you will need to set up the connection parameters, so it knows it must look for the database in our docker container.

This step is pretty straightforward. Double-click the `SYSTEM` database in the upper-left corner. Enter the password you set up earlier as the password and check the "Save password" box.
In the `Host` field, enter `localhost` if the container is running on this machine or the local IP of the machine where the docker image is in your LAN network.
Leave `port` and `SID` to 1521 and xe, respectively.

Now we need to create a user, a new database to host our data and a table where to insert the data.

Use the provided [*.sql files][sqls] for each of these steps.
___

## Setting up the Python Aplication

First, install all the required packages using the `requirements.txt` file:

```console
pip install -r requirements.txt
```

If your `Oracle Database` is installed locally, you are good to go.
In the case you have it remote (like in a docker volume), you will need to download the [OracleClient][OracleClient] locally.
You will have to set the path to the OracleClient in the `EnvironmentVariables.py` file.

[OracleCLient]: https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html
[Apache NiFi]: https://nifi.apache.org/
[Oracle database]: https://hub.docker.com/r/gvenzl/oracle-xe
[HortonWorks Data Flow sandbox]: https://www.cloudera.com/tutorials/sandbox-deployment-and-install-guide/3.html
[Docker]: https://docs.docker.com/get-docker/
[Oracle SQL Developer]: https://www.oracle.com/tools/downloads/sqldev-downloads.html
[sqls]: master/blob