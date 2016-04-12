__author__ = "Mitch Powell"
from flask import Flask, render_template, make_response, request
from models import *

application = app = Flask(__name__)
app.config["DEBUG"] = True


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


@app.route('/', methods=["GET", "POST"])
def root():
    items = sorted([item.item_name for item in Item.select()])
    buildings= sorted([building.build_name for building in Building.select()])
    return render_template('index.html',  items = items, buildings=buildings)


@app.route('/select/', methods=["POST"])
def select():
    in_item = request.form['item']
    building = request.form['building']
    item = Item.select().where(Item.item_name == in_item).get()
    if building != "Any":
        storages = Stored.select()\
            .join(Item)\
            .where(Item.item_name == in_item)\
            .switch(Stored)\
            .join(Storage)\
            .join(Building)\
            .where(Building.build_name == building)
    else:
        storages = Stored.select()\
            .join(Item)\
            .where(Item.item_name == in_item)
    return render_template('storage_search.html', item=item, building=building, storages=storages)


@app.route('/testpage/')
def testpage():
    return render_template('testpage.html')

if __name__ == '__main__':
    app.run()
