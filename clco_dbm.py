import peewee
from peewee import *

#variable used for logging into the appropriate database
closetdb = MySQLDatabase('450project', user = 'naa5728', passwd = 'u8iVfNVL6')

#class Building(Model) creates the table
class Building(Model):
    #PrimaryKeyField designates that build_id is the primary key of type integer
    build_id = PrimaryKeyField(IntegerField())
    build_name = CharField()

    #not clear as to why a meta class needs to be created
    #will look into
    class Meta:
        database = closetdb

class Storage(Model):
    storage_id = PrimaryKeyField(CharField(6))
    build_id = ForeignKeyField(Building)
    storekey_id = ForeignKeyField(StoreKey)
    room_number = CharField(6)
    room_name = CharField(40)

    class Meta:
        order_by = ('storage_id',)

class StoreKey(Model):
    storekey_id = PrimaryKeyField(CharField(6))
    storekey_name = CharField(30)

    class Meta:
        order_by = ('storekey_id', )

'''
These are just some example queries that can be run
using peewee
'''
#Simple insert statement
Building.insert(52134, 'This Building').execute()

#Bulk Insert statement
store_keys = [
    {'id': '1234', 'name': 'storage1'},
    {'id': '5678', 'name': 'storage2'}
]

for data_val in store_keys:
    StoreKey.create(**data_val)

#Select all building names in the building table and print them out
for building in Building.select():
    print (building.build_name)
