alter table campaigns add column hashval varchar(64);
alter table campaigns add unique key hashval (hashval);
