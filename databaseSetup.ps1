#!sqls\setup_database.ps1

$path = (Join-Path $PWD '\scripts\')
$scriptsPath = (($path -replace "\\","/") -replace ":","").ToLower().Trim("/")

if ( Test-Path $path ) 
{
	Write-Output "Directory $path found."

	if ( (Test-Path $(Join-Path $path "1_create_user.sql") ) -and
		(Test-Path $(Join-Path $path "2_connect_user.sql") ) -and
		(Test-Path $(Join-Path $path "3_create_table.sql")) 
	) 
	{ 
		Write-Output "Scripts found" 
	}
	else 
	{
		Write-Output "Missing one or more scripts on $pwd"
		exit 0 
	}

	Write-Output "Pulling Docker image..."
	docker pull gvenzl/oracle-xe:18-slim

	Write-Output "Setting up the docker container..."
	Write-Output "$scriptsPath`:/container-entrypoint-initdb."
	docker run --name earthquakeDB -p 1521:1521 -e ORACLE_PASSWORD="admin" -v $scriptsPath`:/container-entrypoint-initdb.d gvenzl/oracle-xe:18-slim
	Write-Output "Success."
	exit 1
}

else { 
	Write-Output "Directory $path doet not exists."
	Write-Output "Operation failed."
	exit 0 
}