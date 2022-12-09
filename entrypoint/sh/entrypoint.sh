#!/usr/bin/bash
##################################

PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin:/usr/local/sbin:/scripts/EDH_NRT_DOCKER_TEST
export PATH

PACKAGE_NAME=$1
echo "Package name received: ${PACKAGE_NAME}"

SHELLPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
LOGPATH="scripts/${PACKAGE_NAME}/log"

if [[ -d $LOGPATH ]]; then
	echo "Log dicerctory ok -- ${LOGPATH}"
else
	echo "Creating log path ${LOGPATH}"
	$(`mkdir -p ${LOGPATH}`)
	echo $(`ls $LOGPATH`)
fi

declare -a SCRIPTS=(
	"create_db"
	"create_tables"
)

for script in ${SCRIPTS[@]};
do
	echo "Launching impala-shell scripts/${PACKAGE_NAME}/sql/${script}.sql"
	nohup impala-shell -f scripts/${PACKAGE_NAME}/sql/${script}.sql >> "${LOGPATH}/${script}.log" 2>&1
done

echo "Done."