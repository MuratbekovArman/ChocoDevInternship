-- migrate:up
set time zone 'Asia/Almaty';

create table if not exists bookings(
    id uuid primary key,
    pnr varchar (10),
    expires_at timestamptz,
    phone varchar (12),
    email varchar (30),
    offer json not null,
    passengers json not null
);

-- migrate:down
drop table if exists bookings;