create table Building

	(build_id			varchar(6),

	 build_name			varchar(50),

	 primary key (build_id)	

	) ENGINE = InnoDB;

	

create table Item

	(item_id			varchar(6),

	 item_name			varchar(40) not null,

	 item_description	varchar(200),

	 primary key (item_id)

	) ENGINE = InnoDB;

	

create table StoreKey

	(storekey_id				varchar(6),

	 storekey_name				varchar(30),

	 primary key (storekey_id)

	) ENGINE = InnoDB;	

	

create table Storage

	(storage_id			varchar(6),

	 build_id 			varchar(6),

	 room_number			varchar(6),

	 room_name			varchar(40),

	 storekey_id			varchar(6),

	 primary key (storage_id),

	 foreign key (build_id) references Building(build_id) ON DELETE CASCADE,

	 foreign key (storekey_id) references StoreKey(storekey_id) ON DELETE CASCADE

	) ENGINE = InnoDB;

	

create table Stored

	(storage_id			varchar(6),

	 item_id 			varchar(6),

	 item_qty			int unsigned,

	 primary key (storage_id, item_id),

	 foreign key (storage_id) references Storage(storage_id) ON DELETE CASCADE,

	 foreign key (item_id) references Item(item_id) ON DELETE CASCADE

	) ENGINE = InnoDB;

create table User
    (
    user_name varchar(30),
    user_pass char(66),
    primary key (user_name)
     ) ENGINE = InnoDB;
