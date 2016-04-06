from flask import Flask, render_template, make_response
from flask_restful import *
import json
from peewee import *
from models import *

app = Flask(__name__)
api = Api(app)

@app.route('/')
def root():
    return render_template('index.html')

@api.representation('application/json')
@app.route('/storages/')
def storage_names():
    resp = make_response(json.dumps([storage.room_name for storage in Storage.select()]))
    return resp


@api.representation('application/json')
@app.route('/buildings/')
def buildings():
    resp = make_response(json.dumps([building.build_name for building in Building.select()]))
    return resp

if __name__ == '__main__':
    app.run()
