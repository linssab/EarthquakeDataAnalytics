DROP TABLE
EARTHQUAKES;

CREATE TABLE
    EARTHQUAKES(
        time VARCHAR(100),
        latitude VARCHAR(100),
        longitude VARCHAR(100),
        depth VARCHAR(100),
        mag VARCHAR(100),
        magType VARCHAR(100),
        nst VARCHAR(100),
        gap VARCHAR(100),
        dmin VARCHAR(100),
        rms VARCHAR(24),
        net VARCHAR(100),
        id VARCHAR(100),
        updated VARCHAR(100),
        place VARCHAR(100),
        type VARCHAR(100),
        horizontalError VARCHAR(24),
        depthError VARCHAR(24),
        magError VARCHAR(24),
        magNst VARCHAR(24),
        status VARCHAR(100),
        locationSource VARCHAR(100),
        magSource VARCHAR(100)
);

SELECT
    count(*)
FROM
    EARTHQUAKES;

SELECT * FROM EARTHQUAKES;

SELECT
    e.type, e.mag, e.time, e.place
FROM
    EARTHQUAKES e
WHERE
    e.status = 'reviewed'
AND
    e.time 
LIKE 
    '2022-04-08%';