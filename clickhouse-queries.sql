drop table vehicle_health_aggregated;
drop table vehicle_health_processed;

CREATE TABLE IF NOT EXISTS vehicle_health_processed
(
    tripID        Int32,
    deviceID      String,
    timeStamp     DateTime,                 
    accData       String,                    
    gps_speed     Float64,
    battery       Float32,
    cTemp         Float32,
    dtc           Int32,
    eLoad         Float64,
    iat           Int32,
    imap          Int32,
    kpl           Float32,
    maf           Int32,
    rpm           Float64,
    speed         Float64,
    tAdv          Int32,
    tPos          Int32,
    `date`        Date MATERIALIZED toDate(timeStamp)   
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(`date`)                
ORDER BY (deviceID, timeStamp);


CREATE TABLE IF NOT EXISTS vehicle_health_aggregated
(
    `date`              Date,        
    `deviceID`          String,
    `avg_rpm`           Float64,
    `max_rpm`           Float64,
    `avg_engine_load`   Float64,
    `max_coolant_temp`  Float64,
    `records`           UInt32       
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(date)
ORDER BY (deviceID, date);


INSERT INTO vehicle_health_processed
SELECT *
FROM s3(
    's3://aditya-bucket-processed/vehicle_health/part-00000-0ccf7b8e-0ff9-4ee0-bd19-c3cd6a89fce8-c000.snappy.parquet',
    'SECRET KEY',
    'ACCESS KEY',
    'Parquet'
);

INSERT INTO vehicle_health_aggregated
SELECT *
FROM s3(
    's3://aditya-bucket-aggregated/vehicle_health_agg/date=2017-12-23/deviceID=0.0/part-00000-80cbc770-c95f-4fe2-9bc0-22c43ae3a972.c000.snappy.parquet',
    'SECRET KEY',
    'ACCESS KEY',
    'Parquet'
    
);