#define views
drop view if exists shortItem;
create view shortItem as
	select item_id, item_name
	from Item;

drop view if exists storagesAndKeyMatches;
create view storagesAndKeyMatches as
	select storage_id, storekey_id
	from Storage;
	
drop view if exists techStorages;
create view techStorages as
	select storage_id, build_id, room_number, room_name
	from Storage
	where room_name like '%tech%';

#Finds an item containing the input string
#EX: call find_item('xlr')
delimiter $$
DROP PROCEDURE IF EXISTS find_item;
create procedure find_item (IN item_name varchar(40))
	DETERMINISTIC
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
	DETERMINISTIC
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

#Move an item from one storage to another
#EX: call move_item(001, 57008, 57010);
DROP PROCEDURE IF EXISTS move_item;
delimiter $$
create procedure move_item(item_id varchar(6), prev_storage_id varchar(6), new_storage_id varchar(6))
	BEGIN
		declare exit handler for sqlexception
			BEGIN
				ROLLBACK;
			END;
		
		start transaction;
		if exists (select * from (Storage natural join Stored) 
						join Item on Item.item_id = Stored.item_id 
				   where item_id = Item.item_id and prev_storage_id = Stored.storage_id)
		
		then 
			update Stored
			set storage_id = new_storage_id
			where storage_id = prev_storage_id and item_id = Stored.item_id;
		end if;
		commit;
	END$$
delimiter ;

#Return the total number of items in the given storage
#EX: select numItems(57010);
drop function if exists numItems;
delimiter $$
create function numItems(storage_id varchar(6))
	returns int unsigned
	DETERMINISTIC
	BEGIN
		declare count int unsigned default 0;
		set count = 0;
		select count(item_id) into count
		from Stored 
		where storage_id = Stored.storage_id
		group by storage_id;
		
		RETURN count;
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
