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
def root(messages=None):
    items = sorted([item.item_name for item in Item.select()])
    buildings = sorted([building.build_name for building in Building.select()])
    return render_template('index.html', items=items, buildings=buildings, messages=messages)


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
# Generates an Item Report page
###
@app.route('/item-reports/')
def item_audit():
    cursor = database.get_cursor()
    query = "SELECT item_id, total from totalItemQty"
    cursor.execute(query)
    allitems = Item.select()
    itemnames = sorted([item.item_name for item in allitems])
    itemlist = {}
    itemquants = {}
    for item, quant in cursor:
        itemquants[item] = quant
    for entity in allitems:
        itemlist[entity.item_name] = {
            'quantity': itemquants[entity.get_id()]
        }

    return render_template('itemaudit.html', itemlist=itemlist, itemnames=itemnames)


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
    return render_template('move.html', storages=storages, items=items)


###
# This function is used to complete the move method once the storage is selected
###
@app.route('/move-from/', methods=['POST'])
def move_from():
    storage_name = request.form['storage']
    storage_items = [entity.item.item_name
                     for entity in Stored.select().join(Storage).where(Storage.room_name == storage_name)]
    to_storages = [storage.room_name
                   for storage in Storage.select().where(Storage.room_name != storage_name)]
    return render_template("movefrom.html", storage_name=storage_name, storage_items=storage_items,
                           to_storages=to_storages)


###
# This function submits the final changes of a move operation to the database
###
@app.route('/submit-move/<storage_name>', methods=['POST'])
def submit_move(storage_name):
    number = request.form['quantity']
    item = Item.get(Item.item_name == request.form['item'].strip()).get_id()
    print item
    to_storage = Storage.get(Storage.room_name == request.form['toStorage'].strip()).get_id()
    from_storage = Storage.get(Storage.room_name == storage_name.strip()).get_id()
    procargs=(item,from_storage,to_storage,number)
    cursor = database.get_cursor()
    cursor.callproc("move_item",procargs)
    cursor.close()
    return root("Item Successfully moved")


###
# This function routes to the Add New Item Type button in the Updates menu
###
@app.route('/newitem/')
def add_new_item():
    return render_template("newitem.html")


###
# Finalizes the submission of a new item type
###
@app.route('/submit-new-item/',methods=['POST'])
def submit_new_item():
    item_name = request.form['itemName'].strip()
    if len(item_name) == 0:
        message = "Please Enter a Valid Item Name"
        return render_template("newitem.html", message=message)
    else:
        try:
            Item.create(
                item_name=request.form['itemName'].strip(),
                item_description=request.form['itemDescription'].strip()
            )
        except IntegrityError:
            message = "Item '"+item_name+"' already exists."
            return render_template("newitem.html", message=message)
    return root("Item Type Added!")


###
# This function routes to the Add Item to Storage button in the updates menu
###
@app.route('/additem/')
def add_to_storage():
    items = [items.item_name for items in Item.select()]
    itemtoAdd = request.form['item']
    storagetoInsert = request.form['storage']
    for item in items:
        stored = Stored.select().join(Item).group_by(Stored.item)
        if itemtoAdd != stored.item:
            storagetoInsert.insert(itemtoAdd)
    return render_template("additem.html")


###
# This function routes to the Remove Item from Storage button in the updates menu
###
@app.route('/removeitem/')
def remove_from_storage():
    storages = sorted([storage.room_name for storage in Storage.select()])
    return render_template("removeitem.html", storages=storages)


###
# This function routes to the removal page once a storage has been selected
###
@app.route("/remove-from/", methods = ["POST"])
def remove_from_selected():
    storage_name = request.form['storage']
    storage_items = [entity.item.item_name
                     for entity in Stored.select().join(Storage).where(Storage.room_name == storage_name)]
    return render_template("removefrom.html", storage_name=storage_name, storage_items=storage_items)


###
# This function is triggered when items are selected to be removed from a storage
###
@app.route('/submit-remove/<storage_name>', methods=["POST"])
def submit_remove(storage_name):
    storage = Storage.get(Storage.room_name == storage_name)
    item = Item.get(Item.item_name == request.form['item'])
    stored = Stored.get(Stored.storage == storage, Stored.item == item)
    print(stored.item_qty)
    if stored.item_qty < int(request.form['quantity']):
        storage_items = [entity.item.item_name for entity in Stored.select().join(Storage)
            .where(Storage.room_name == storage_name)]
        return render_template('removefrom.html', storage_name=storage_name, storage_items=storage_items,
                               warnings="There are not that many "+request.form['item']+"s in the storage")
    elif stored.item_qty == int(request.form['quantity']):
        stored.delete_instance()
        return root("All "+request.form['item']+"s successfuly removed from "+storage_name)
    else:
        stored.item_qty = (stored.item_qty - int(request.form['quantity']))
        stored.save()
        return root(request.form['quantity']+" "+request.form['item']+"s successfully removed from "+storage_name)


###
# This function generates a sorted list of storage names for a given building
###
def get_storages(building_name):
    return sorted([storage.room_name for storage in
                   Storage.select().join(Building).where(Building.build_name == building_name)])


if __name__ == '__main__':
    app.run()
