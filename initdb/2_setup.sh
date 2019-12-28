#!/bin/bash
psql -U postgres -d himitsu_lun_db << "EOSQL"
create table himitsu_lun_table (
    id integer PRIMARY KEY SERIAL,
    filename varchar(255) not null,
    enc_filename varchar(255) not null,
    share_id integer not null,
    share varchar(255) not null,
    created_at timestamp not null,
    delete_at timestamp not null);
EOSQL