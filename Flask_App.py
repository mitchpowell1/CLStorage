__author__ = "Mitch Powell"
from flask import Flask, render_template, make_response, request
from models import *

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=["GET", "POST"])
def root():
    items = sorted([item.item_name for item in Item.select()])
    buildings= sorted([building.build_name for building in Building.select()])
    return render_template('index.html',  items = items, buildings=buildings)


@app.route('/select/', methods=["POST"])
def select():
    in_item = request.form['item']
    building = request.form['building']
    item = Item.get(Item.item_name == in_item).item
    storages = Storage.select(Storage.room_name, Storage.room_number).join(Stored.select(Stored.item_qty).where(Stored. == item).get())
    for storage_entry in storages:
        print storage_entry.room_name
    print item.item
    return render_template('storage_search.html', item=in_item,  building = building)


@app.route('/testpage/')
def testpage():
    return render_template('testpage.html')

if __name__ == '__main__':
    app.run()
