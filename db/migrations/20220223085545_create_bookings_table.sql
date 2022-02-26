-- migrate:up
create table if not exists bookings(
    id varchar(36) primary key,
    pnr varchar (6),
    expires_at varchar (50),
    phone varchar (12),
    email varchar (30),
    offer json not null,
    passengers json not null
);

-- migrate:down
drop table if exists bookings;