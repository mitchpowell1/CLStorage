#define views
create view shortItem as
	select item_id, item_name
	from Item;
	
create view storagesAndKeyMatches as
	select storage_id, storekey_id
	from Storage;
	
create view techStorages as
	select storage_id, build_id, room_number, room_name
	from Storage
	where room_name like '%tech%';

#Finds an item containing the input string
#EX: call find_item('xlr')
delimiter $$
DROP PROCEDURE IF EXISTS find_item;
create procedure find_item (IN item_name varchar(40))
	BEGIN
		(select Item.item_id, Item.item_name, Storage.storage_id, Storage.room_number, Storage.build_id
		 from (Storage natural join Stored) join Item on Item.item_id = Stored.item_id
		 where Item.item_name like CONCAT('%', item_name, '%'));
	END$$
delimiter ;

#Calculates the total amount  of each item and updates the Item table.
#EX: call find_total()
delimiter $$
DROP PROCEDURE IF EXISTS find_total;
create procedure find_total ()
	BEGIN
		create temporary table TempTable (item_id varchar(6),total_qty int);
		insert into TempTable (select item_id, sum(item_qty) from Stored group by item_id);
		
		 if exists (select * from information_schema.columns where table_name = 'Item' and column_name = 'total_qty') 
			then alter table Item drop column total_qty;
		 end if;
		alter table Item ADD total_qty int unsigned NOT NULL default 0;
		
		update Item
		Item inner join TempTable on Item.item_id = TempTable.item_id
		set Item.total_qty = TempTable.total_qty;
		
		drop table TempTable;
	END$$
delimiter ;

#Update the total qty of the items after an update or addition of an item
drop trigger if exists updateTotal;
delimiter $$
create trigger updateTotal after update on Stored
	FOR EACH ROW
	BEGIN
		call find_total();
	END$$
	
delimiter ;

drop trigger if exists updateTotal2;
delimiter $$
create trigger updateTotal2 after insert on Stored
	FOR EACH ROW
	BEGIN
		call find_total();
	END$$
	
delimiter ;

call find_total();
