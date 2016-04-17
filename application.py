from flask import Flask, render_template, request, session
from models import *
from werkzeug.security import check_password_hash

application = app = Flask(__name__)
app.config["DEBUG"] = True

session_key = open("SESSION_KEY", 'r').read().strip()

app.secret_key = session_key

__author__ = "Mitch Powell"


###
# This function should be called any time a request is sent.
# It should prevent the database connection from timing out after
# the app has been running for a few days.
###
@app.before_request
def establish_connection():
    database.connect()


###
# This function should be called any time a request is finished executing.
# It will close the database connection so that the connection isn't
# just sitting around idle.
###
@app.teardown_request
def close_connection(exc):
    if not database.is_closed():
        database.close()


###
# This function routes to the homepage of the application
# It renders a template containing two select boxes, corresponding with
# the different available items and buildings respectively.
###
@app.route('/', methods=["GET", "POST"])
def root():
    items = sorted([item.item_name for item in Item.select()])
    buildings = sorted([building.build_name for building in Building.select()])
    return render_template('index.html', items=items, buildings=buildings)


###
# This function returns the results page for a storage search.
###
@app.route('/select/', methods=["POST"])
def select():
    in_item = request.form['item']
    building = request.form['building']
    item = Item.select().where(Item.item_name == in_item).get()
    if building != "Any":
        storages = Stored.select() \
            .join(Item) \
            .where(Item.item_name == in_item) \
            .switch(Stored) \
            .join(Storage) \
            .join(Building) \
            .where(Building.build_name == building)
    else:
        storages = Stored.select() \
            .join(Item) \
            .where(Item.item_name == in_item)
    return render_template('storage_search.html', item=item, building=building, storages=storages)


###
# This function renders a template with a selector box for every storage,
# separated by building labels
###
@app.route('/storage-reports/')
def storage_audit():
    storages = {}
    for building in ["Fisher Student Center", "Fisher University Union", "Burney Center", "Warwick Center"]:
        storages[building] = get_storages(building)

    return render_template('audit.html', storages=storages)


###
# This function renders a template for a storage audit, which tells all of the information about
# a particular storage
###
@app.route('/generate-audit/', methods=["POST"])
def gen_audit():
    st_name = request.form['storage']
    storage = Storage.select().where(Storage.room_name == st_name)
    stored = Stored.select().join(Storage).where(Storage.room_name == st_name)
    room_items = []
    room_qts = []
    for entity in stored:
        room_items.append(entity.item.item_name)
        room_qts.append(entity.item_qty)
    room_data = \
        {
            "name": storage[0].room_name,
            "key": storage[0].storekey.storekey_name,
            "building": storage[0].build.build_name,
            "number": storage[0].room_number,
            "items": room_items,
            "quantities": room_qts,
            "numitems": len(room_items)
        }
    return render_template("storage_report.html", room_data=room_data)


###
# This function is triggered when a user is logged into the CLCO system
###
@app.route('/login/', methods=["POST"])
def user_login():
    username = request.form['username']
    user = User.get(User.user_name == username)
    if check_password_hash(user.user_pass, request.form['password']):
        print("login successful")
        session['loggedin'] = True
    else:
        print("login unsuccessful")
    return root()


###
# This function logs the user out, and adjusts session variables accordingly
###
@app.route('/logout/')
def user_logout():
    session['loggedin'] = False
    return root()


###
# This function corresponds with functionality to move items from one storage to another
###
@app.route('/move/')
def move():
    storages = [storage.room_name for storage in Storage.select()]
    items = {}
    for storage in storages:
        stored = Stored.select().join(Storage).where(Storage.room_name == storage)
        items[storage] = {entity.item.item_name: entity.item_qty for entity in stored}
        print storage, items[storage]
    print items["Burney Storage"]['Chair']
    return render_template('move.html', storages=storages)


###
# This function routes to the Add New Item Type button in the Updates menu
###
@app.route('/newitem/')
def add_new_item():
    return render_template("newitem.html")


###
# This function routes to the Add Item to Storage button in the updates menu
###
@app.route('/additem/')
def add_to_storage():
    return render_template("additem.html")


###
# This function routes to the Remove Item from Storage button in the updates menu
###
@app.route('/removeitem/')
def remove_from_storage():
    return render_template("removeitem.html")


###
# This function generates a sorted list of storage names for a given building
###
def get_storages(building_name):
    return sorted([storage.room_name for storage in
                   Storage.select().join(Building).where(Building.build_name == building_name)])


if __name__ == '__main__':
    app.run()
