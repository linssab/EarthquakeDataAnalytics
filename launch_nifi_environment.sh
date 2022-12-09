
declare -i COUNTER=0

SCRIPTS_PATH="${PWD}/scripts"

if [[ -d "$SCRIPTS_PATH" ]]
then
	echo "Directory ${SCRIPTS_PATH} found."
	
	for entry in "$SCRIPTS_PATH"/*
	do
		if [[ $entry == *.sql || $entry == *.sh ]]
		then
			COUNTER+=1
			echo "Found a script: $entry"
		fi
	done
	
	echo "Script will execute $COUNTER user scripts inside the database image."
	echo "Continuing with the operation."
	
else
	echo "Directory ${SCRIPTS_PATH} does not exist."
	echo "Continuing without custom sql/sh scripts."
fi 

echo "Building containers..."
docker-compose build
RETURN=$?

if [[ $RETURN != 0 ]]
then
	echo "Failed to build the containers..."
	exit 1
else
	echo "Starting up the containers"
	docker-compose up -d
	docker exec nifi_container mkdir collected_data/usgs-data
	docker exec nifi_container mkdir opt
	docker cp ./drivers/* nifi_container:/opt
	echo "Done."
fi 
