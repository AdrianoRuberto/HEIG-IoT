create keyspace if not exists data
with replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use data;

create table events (
    event_id uuid primary key,
    parking int,
    timestamp timestamp,
    device ascii,
    type ascii,
    vehicle_id ascii,
    extra map<ascii, ascii>
);
