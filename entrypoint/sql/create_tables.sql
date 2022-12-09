DROP TABLE IF EXISTS LOG.log_errore;
DROP TABLE IF EXISTS LOG.log_elab;
DROP TABLE IF EXISTS WORK.earthquakes;

CREATE TABLE WORK.earthquakes (
	time_elab TIMESTAMP,
	id STRING,
	time TIMESTAMP, 
	latitude STRING, 
	longitude STRING, 
	depth DOUBLE, 
	mag DOUBLE, 
	magType STRING, 
	nst STRING,
	rms STRING,
	net STRING,
	updated STRING,
	place STRING,
	type STRING,
	horizontalError STRING,
	depthError DOUBLE,
	magError DOUBLE,
	magNst DOUBLE,
	status STRING,
	locationSource STRING,
	magSource STRING,
	PRIMARY KEY(time_elab, id)
--	) STORED AS KUDU TBLPROPERTIES ('kudu.master_addresses' = '80.181.218.42', 'kudu.num_tablet_replicas' = '1');
	) STORED AS KUDU TBLPROPERTIES ('kudu.master_addresses' = '127.0.0.1', 'kudu.num_tablet_replicas' = '1');
	
CREATE TABLE LOG.log_elab (
	nome_file STRING,
	data_elab TIMESTAMP,
	tipo STRING,
	PRIMARY KEY(nome_file, data_elab)
--	) STORED AS KUDU TBLPROPERTIES ('kudu.master_addresses' = '80.181.218.42', 'kudu.num_tablet_replicas' = '1');
	) STORED AS KUDU TBLPROPERTIES ('kudu.master_addresses' = '127.0.0.1', 'kudu.num_tablet_replicas' = '1');

CREATE TABLE LOG.log_errore (
	time_elab STRING,
	id STRING,
	time STRING, 
	latitude STRING, 
	longitude STRING, 
	depth DOUBLE, 
	mag DOUBLE, 
	magType STRING, 
	nst STRING,
	rms STRING,
	net STRING,
	updated STRING,
	place STRING,
	type STRING,
	horizontalError STRING,
	depthError DOUBLE,
	magError DOUBLE,
	magNst DOUBLE,
	status STRING,
	locationSource STRING,
	magSource STRING
	) STORED AS PARQUET LOCATION '/user/hive/warehouse/ingestion_db2.db/log_errore' TBLPROPERTIES('parquet.compress'='snappy');
	