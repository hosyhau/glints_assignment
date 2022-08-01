# Prerequisite server requirement (Linux)
## Docker & Docker compose installation
### Install Docker in Ubuntu server (For the other servers type, please install via link: https://docs.docker.com/engine/install/)
Uninstall old versions
Older versions of Docker were called docker, docker.io, or docker-engine. If these are installed, uninstall them:
```
sudo apt-get remove docker docker-engine docker.io containerd runc
```
Set up the repository
```
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```
Add Docker’s official GPG key:
```
sudo mkdir -p /etc/apt/keyrings
 curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```
Use the following command to set up the repository:
```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
Install Docker Engine
```
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo docker --version
```
You’ll see output similar to this:
```
Docker version 20.10.16, build aa7e414
```
### Install Docker compose
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```
You’ll see output similar to this:
```
Output
docker-compose version 1.29.2, build 5becea4c
```

# Get the code & Run the docker-compose
## Get the public code via link: https://github.com/hosyhau/glints_assignment
```
git clone https://github.com/hosyhau/glints_assignment
```
## Run the docker container
```
cd glints
sudo docker-compose up -d --remove-orphans
```
You’ll see output similar to this:
```
Creating network "glints_default" with the default driver
Creating airflow-init ... done
Creating target_db    ... done
Creating postgres     ... done
Creating source_db    ... done
Creating airflow-scheduler ... done
Creating airflow-webserver ... done
```
Checking the container is running:
```
sudo docker container list
```
You’ll see output similar to this:
```
CONTAINER ID   IMAGE                  COMMAND                  CREATED              STATUS                                 PORTS                                                 NAMES
35b7c78d6c10   apache/airflow:2.3.0   "/usr/bin/dumb-init …"   About a minute ago   Up About a minute (health: starting)   0.0.0.0:5884->8080/tcp, :::5884->8080/tcp             airflow-webserver
b80ff42f468e   apache/airflow:2.3.0   "/usr/bin/dumb-init …"   About a minute ago   Up About a minute                      8080/tcp, 0.0.0.0:8793->8793/tcp, :::8793->8793/tcp   airflow-scheduler
7825c6b2b699   postgres:13            "docker-entrypoint.s…"   About a minute ago   Up About a minute (healthy)            0.0.0.0:5432->5432/tcp, :::5432->5432/tcp             postgres
d0ff9e53d6f3   postgres:13            "docker-entrypoint.s…"   About a minute ago   Up About a minute                      0.0.0.0:5434->5432/tcp, :::5434->5432/tcp             source_db
ac092a00e769   postgres:13            "docker-entrypoint.s…"   About a minute ago   Up About a minute                      0.0.0.0:5433->5432/tcp, :::5433->5432/tcp             target_db
```

# Open Airflow UI & Config Postgres connection
## Open Airflow UI
Go to the URI: localhost: http://localhost:5884/
```
Enter username: airflow
Enter password: airflow
```
## Add source & target postgres connection
Go to this link: http://localhost:5884/connection/add
### For source db connection:
```
Connection Id: source_db
Connection Type: Postgres
Host: Enter your IP v4 of your computer
Schema: source
Login: source_user
Password: source_password
Port: 5434
```
### For target db connection:
```
Connection Id: target_db
Connection Type: Postgres
Host: Enter your IP v4 of your computer
Schema: target
Login: target_user
Password: target_password
Port: 5433
```

# Trigger etl_dag
## Navigate to the DAGs tab, please click into dag_id etl_dag button to make it active dag
## Trigger DAG by click the trigger button in right tab Actions.
##Notes:
The Dag will pull the source DB to target DB every 5mins.
In the target database: It has two table, first one is sale table from source, the second one is job table, it is a metadata table to store the log pulling records from source DB