CREATE USER earthquake_manager IDENTIFIED BY admin;
GRANT CONNECT TO earthquake_manager;
GRANT CONNECT, RESOURCE, DBA TO earthquake_manager;
GRANT UNLIMITED TABLESPACE TO earthquake_manager;