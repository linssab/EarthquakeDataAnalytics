#setup_database.sh

SCRIPTS_PATH="${PWD}/scripts"

if [[ -d "$SCRIPTS_PATH" ]]
then
	echo "Directory ${SCRIPTS_PATH} found."

	if [ -f "${SCRIPTS_PATH}/1_create_user.sql" ] &&
		[ -f "${SCRIPTS_PATH}/2_connect_user.sh" ] &&
		[ -f "${SCRIPTS_PATH}/3_create_table.sql" ];
	then
		echo "Scripts found" 
	else 
		[ -f "${SCRIPTS_PATH}/1_create_user.sql" ] && pass || echo "Missing script 1_create_user.sql"
		[ -f "${SCRIPTS_PATH}/2_connect_user.sh" ] && pass || echo "Missing script 2_connect_user.sql"
		[ -f "${SCRIPTS_PATH}/3_create_table.sql" ] && pass || echo "Missing script 3_create_table.sql"
		echo "Missing one or more scripts on ${SCRIPTS_PATH}"
		exit 0
	fi

	echo "Pulling Docker image..."
	docker pull gvenzl/oracle-xe:18-slim

	echo "Setting up the docker container..."
	echo "Entry point: $SCRIPTS_PATH"
	docker run --name earthquakeDB1 -p 1521:1521 -e ORACLE_PASSWORD="admin" -v /${SCRIPTS_PATH}:/container-entrypoint-initdb.d gvenzl/oracle-xe:18-slim
	echo "Success."
	exit 1

else
	echo "Directory ${SCRIPTS_PATH} does not exists."
	echo "Operation failed."
	exit 0 
fi