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

#Move an item from one storage to another
#EX: call move_item(42,57008, 57001, 6);
DROP PROCEDURE IF EXISTS move_item;
delimiter $$
create procedure move_item(item_id varchar(6), prev_storage_id varchar(6), new_storage_id varchar(6), quantity int unsigned)
	BEGIN
		declare qty_comp int unsigned;
		declare exit handler for sqlexception
			BEGIN
				ROLLBACK;
			END;
		start transaction;

		if exists (select * 
				from Stored
				where storage_id = prev_storage_id and Stored.item_id = item_id)		
		
		then 
		
		select item_qty 
			into qty_comp
			from Stored 
			where item_id = Stored.item_id and prev_storage_id = Stored.storage_id;
			
			if (quantity >= qty_comp)
			then
				
				if exists(select * 
						from Stored 
						where storage_id = new_storage_id and Stored.item_id = item_id)
				then
					
					update Stored
					set Stored.item_qty = Stored.item_qty + qty_comp
					where storage_id = new_storage_id and item_id = Stored.item_id;
					
					delete from Stored
					where storage_id = prev_storage_id and item_id = Stored.item_id;
					
				else
				
					update Stored
					set storage_id = new_storage_id
					where storage_id = prev_storage_id and item_id = Stored.item_id;
				
				end if;
				
			else
			
				if exists(select * 
						from Stored 
						where storage_id = new_storage_id and Stored.item_id = item_id)
				then
					update Stored
					set Stored.item_qty = Stored.item_qty + quantity
					where storage_id = new_storage_id and item_id = Stored.item_id;
				else
					insert into Stored values
						(new_storage_id, item_id, quantity);
				end if;
				
				update Stored
				set Stored.item_qty = Stored.item_qty - quantity
				where storage_id = prev_storage_id and item_id = Stored.item_id;
				
			end if;
			
		else
			select 'No item exists in given storage to move';
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
	
