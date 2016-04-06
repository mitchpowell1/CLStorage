from models import *
from peewee import *

for building in Building.select():
    print building.build, building.build_name
