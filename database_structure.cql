create keyspace if not exists data
with replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use data;

create table events (
    event_id uuid,
    parking int,
    timestamp timestamp,
    device ascii,
    type ascii,
    vehicle_id ascii,
    extra map<ascii, ascii>,
    primary key(event_id)
);

create table park_stat_delta (
    parking int,
    timestamp timestamp,
    delta int,
    primary key(parking, timestamp)
);

create table park_stat (
    parking int,
    timestamp timestamp,
    count int,
    primary key(parking, timestamp)
);

create table park_occupation (
    parking int,
    occupation int,
    primary key(parking)
);