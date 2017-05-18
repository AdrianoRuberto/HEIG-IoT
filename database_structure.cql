# requires keyspace input_data to exist

create keyspace data
with replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use input_data;

create table events (
    parking int,
    timestamp timestamp,
    device ascii,
    type ascii,
    vehicle_id ascii,
    extra map<ascii, ascii>
);
