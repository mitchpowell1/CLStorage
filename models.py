from peewee import *

database = MySQLDatabase('mdp9648', **{'password': '', 'user': 'root'})

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
    item = CharField(db_column='item_id', primary_key=True)
    item_name = CharField()

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
    in_ = CharField(db_column='in_id', primary_key=True)
    item = ForeignKeyField(db_column='item_id', null=True, rel_model=Item, to_field='item')
    item_qty = IntegerField(null=True)
    storage = ForeignKeyField(db_column='storage_id', null=True, rel_model=Storage, to_field='storage')

    class Meta:
        db_table = 'Stored'

