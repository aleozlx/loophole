create table tuser(
	name        text primary key not null,
	passwd      text not null
);
insert into tuser (name,passwd) values('admin','0000');
