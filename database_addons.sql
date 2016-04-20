#Define views
#Note: totalItemQty view is after findItemQty function
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

#Return the total quantity of a particular item (from all storages)
#Ex: select item_id, findItemQty(item_id) from Item;
drop function if exists findItemQty;
delimiter $$
create function findItemQty(search_id varchar(6))
	returns int unsigned
	DETERMINISTIC
	BEGIN
		declare count int unsigned default 0;
		set count = 0;
		
		select sum(item_qty) into count
			from Stored
			where search_id = item_id
			group by item_id;
		return count;
	END$$
delimiter ;

drop view if exists totalItemQty;
create view totalItemQty as
	select item_id, findItemQty(item_id) as total
	from Item;

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

create table Tracking
	(log_id 	INT NOT NULL AUTO_INCREMENT,
	 table_name 		varchar(50),
	 attribute				varchar(50),
	 old_value 			varchar(100),
	 new_value			varchar(100),
	 time_changed		datetime not null,
	 primary key(log_id)
	 )ENGINE = InnoDB;
	 
ALTER TABLE Tracking AUTO_INCREMENT=1001;
	 
drop trigger if exists storedUpdate;
delimiter $$
create trigger storedUpdate after update on Stored
	FOR EACH ROW
	BEGIN
		if (NEW.storage_id != OLD.storage_id)then
			insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
				('Stored', 'storage_id', OLD.storage_id, NEW.storage_id, NOW());
		end if;
		
		if (NEW.item_id != OLD.item_id)then
			insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values
				('Stored', 'item_id', OLD.item_id, NEW.item_id, NOW());
		end if;
		
		if(NEW.item_qty != OLD.item_qty)then
			insert into Tracking (table_name, attribute, old_value, new_value, time_changed) values
				('Stored', 'item_id', OLD.item_qty, new.item_qty, NOW());
		end if;
	END$$
delimiter ;

drop trigger if exists storedInsert;
delimiter $$
create trigger storedInsert after insert on Stored
	FOR EACH ROW
	BEGIN
		insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
			('Stored', 'Insertion', 'Insertion', NEW.storage_id, NOW());

	END$$
delimiter ;

drop trigger if exists storedDelete;
delimiter $$
create trigger storedDelete after delete on Stored
	FOR EACH ROW
	BEGIN
		insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
			('Stored', 'Deletion', OLD.storage_id, 'Deletion', NOW());
		
	END$$
delimiter ;

drop trigger if exists itemUpdate;
delimiter $$
create trigger itemUpdate after update on Item
	FOR EACH ROW
	BEGIN
		if (NEW.item_id != OLD.item_id)then
			insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
				('Item', 'item_id', OLD.item_id, NEW.item_id, NOW());
		end if;
		
		if (NEW.item_name != OLD.item_name)then
			insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values
				('Item', 'item_name', OLD.item_name, NEW.item_name, NOW());
		end if;
		
		if(NEW.item_description != OLD.item_description)then
			insert into Tracking (table_name, attribute, old_value, new_value, time_changed) values
				('Item', 'item_description', OLD.item_description, new.item_description, NOW());
		end if;
	END$$
delimiter ;

drop trigger if exists itemInsert;
delimiter $$
create trigger itemInsert after insert on Item
	FOR EACH ROW
	BEGIN
		insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
			('Item', 'Insertion', 'Insertion', NEW.item_id, NOW());

	END$$
delimiter ;

drop trigger if exists itemDelete;
delimiter $$
create trigger itemDelete after delete on Item
	FOR EACH ROW
	BEGIN
		insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
			('Item', 'Deletion', OLD.item_id, 'Deletion', NOW());
		
	END$$
delimiter ;

drop trigger if exists storageUpdate;
delimiter $$
create trigger storageUpdate after update on Storage
	FOR EACH ROW
	BEGIN
		if (NEW.storage_id != OLD.storage_id)then
			insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
				('Storage', 'storage_id', OLD.storage_id, NEW.storage_id, NOW());
		end if;
		
		if (NEW.build_id != OLD.build_id)then
			insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values
				('Storage', 'build_id', OLD.build_id, NEW.build_id, NOW());
		end if;
		
		if(NEW.room_number != OLD.room_number)then
			insert into Tracking (table_name, attribute, old_value, new_value, time_changed) values
				('Storage', 'room_number', OLD.room_number, new.room_number, NOW());
		end if;
		
		if(NEW.room_name != OLD.room_name)then
			insert into Tracking (table_name, attribute, old_value, new_value, time_changed) values
				('Storage', 'room_name', OLD.room_name, new.room_name, NOW());
		end if;
		
		if(NEW.storekey_id != OLD.storekey_id)then
			insert into Tracking (table_name, attribute, old_value, new_value, time_changed) values
				('Storage', 'storekey_id', OLD.storekey_id, new.storekey_id, NOW());
		end if;
	END$$
delimiter ;

drop trigger if exists storageInsert;
delimiter $$
create trigger storageInsert after insert on Storage
	FOR EACH ROW
	BEGIN
		insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
			('Storage', 'Insertion', 'Insertion', NEW.storage_id, NOW());

	END$$
delimiter ;

drop trigger if exists storageDelete;
delimiter $$
create trigger storageDelete after delete on Storage
	FOR EACH ROW
	BEGIN
		insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
			('Storage', 'Deletion', OLD.storage_id, 'Deletion', NOW());
		
	END$$
delimiter ;
		
drop trigger if exists buildingUpdate;
delimiter $$
create trigger buildingUpdate after update on Building
	FOR EACH ROW
	BEGIN
		if (NEW.build_id != OLD.build_id)then
			insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
				('Building', 'build_id', OLD.build_id, NEW.build_id, NOW());
		end if;
		
		if (NEW.build_name != OLD.build_name)then
			insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values
				('Building', 'build_name', OLD.build_name, NEW.build_name, NOW());
		end if;
		
	END$$
delimiter ;

drop trigger if exists buildingInsert;
delimiter $$
create trigger buildingInsert after insert on Building
	FOR EACH ROW
	BEGIN
		insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
			('Building', 'Insertion', 'Insertion', NEW.build_id, NOW());

	END$$
delimiter ;

drop trigger if exists buildingDelete;
delimiter $$
create trigger buildingDelete after delete on Building
	FOR EACH ROW
	BEGIN
		insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
			('Building', 'Deletion', OLD.build_id, 'Deletion', NOW());
		
	END$$
delimiter ;

drop trigger if exists storekeyUpdate;
delimiter $$
create trigger storekeyUpdate after update on StoreKey
	FOR EACH ROW
	BEGIN
		if (NEW.storekey_id != OLD.storekey_id)then
			insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
				('StoreKey', 'storekey_id', OLD.storekey_id, NEW.storekey_id, NOW());
		end if;
		
		if (NEW.storekey_name != OLD.storekey_name)then
			insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values
				('StoreKey', 'storekey_name', OLD.storekey_name, NEW.storekey_name, NOW());
		end if;
		
	END$$
delimiter ;

drop trigger if exists storekeyInsert;
delimiter $$
create trigger storekeyInsert after insert on StoreKey
	FOR EACH ROW
	BEGIN
		insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
			('StoreKey', 'Insertion', 'Insertion', NEW.storekey_id, NOW());

	END$$
delimiter ;

drop trigger if exists storekeyDelete;
delimiter $$
create trigger storekeyDelete after delete on StoreKey
	FOR EACH ROW
	BEGIN
		insert into Tracking(table_name, attribute, old_value, new_value, time_changed) values 
			('StoreKey', 'Deletion', OLD.storekey_id, 'Deletion', NOW());
		
	END$$
delimiter ;
