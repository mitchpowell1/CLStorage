"""
This file defines the classes corresponding with mysql tables for the PeeWee ORM.
"""
from peewee import *

__author__ = "Mitch Powell"


database = MySQLDatabase('mdp9648', **{'user': 'app'})


class UnknownField(object):
    pass


class BaseModel(Model):
    class Meta:
        database = database


class Building(BaseModel):
    build = CharField(db_column='build_id', primary_key=True)
    build_name = CharField(null=True)

    class Meta:
        db_table = 'Building'


class Item(BaseModel):
    item_description = CharField(null=True)
    item = PrimaryKeyField(db_column='item_id')
    item_name = CharField(unique=True)

    class Meta:
        db_table = 'Item'


class Storekey(BaseModel):
    storekey = CharField(db_column='storekey_id', primary_key=True)
    storekey_name = CharField(null=True)

    class Meta:
        db_table = 'StoreKey'


class Storage(BaseModel):
    build = ForeignKeyField(db_column='build_id', null=True, rel_model=Building, to_field='build')
    room_name = CharField(null=True)
    room_number = CharField(null=True)
    storage = CharField(db_column='storage_id', primary_key=True)
    storekey = ForeignKeyField(db_column='storekey_id', null=True, rel_model=Storekey, to_field='storekey')

    class Meta:
        db_table = 'Storage'


class Stored(BaseModel):
    item = ForeignKeyField(db_column='item_id', rel_model=Item, to_field='item')
    item_qty = IntegerField(null=True)
    storage = ForeignKeyField(db_column='storage_id', rel_model=Storage, to_field='storage')

    class Meta:
        db_table = 'Stored'
        indexes = (
            (('storage', 'item'), True),
        )
        primary_key = CompositeKey('item', 'storage')


class Tracking(BaseModel):
    attribute = CharField(null=True)
    log = PrimaryKeyField(db_column='log_id')
    new_value = CharField(null=True)
    old_value = CharField(null=True)
    table_name = CharField(null=True)
    time_changed = DateTimeField()

    class Meta:
        db_table = 'Tracking'


class User(BaseModel):
    user_name = CharField(primary_key=True)
    user_pass = CharField(null=True)

    class Meta:
        db_table = 'User'


class Shortitem(BaseModel):
    item = IntegerField(db_column='item_id')
    item_name = CharField()

    class Meta:
        db_table = 'shortItem'


class Storagesandkeymatches(BaseModel):
    storage = CharField(db_column='storage_id')
    storekey = CharField(db_column='storekey_id', null=True)

    class Meta:
        db_table = 'storagesAndKeyMatches'


class Techstorages(BaseModel):
    build = CharField(db_column='build_id', null=True)
    room_name = CharField(null=True)
    room_number = CharField(null=True)
    storage = CharField(db_column='storage_id')

    class Meta:
        db_table = 'techStorages'


class Totalitemqty(BaseModel):
    item = IntegerField(db_column='item_id')
    total = IntegerField(null=True)

    class Meta:
        db_table = 'totalItemQty'
