from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")


db = SQLAlchemy(app)
ma = Marshmallow(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String)
    item_img = db.Column(db.String, unique=True)

    def __init__(self, name, type, item_img):
        self.name = name
        self.type = type
        self.item_img = item_img

#SCHEMAS---------------------------------------------------SCHEMAS

class ItemSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'type', 'item_img')

item_schema = ItemSchema()
multi_item_schema = ItemSchema(many=True)

#POSTS-------------------------------------------------------POSTS

@app.route('/item/add', methods=["POST"])
def add_item():
    if request.content_type != 'application/json':
        return jsonify('Error: must be JSON')

    post_data = request.get_json()
    name = post_data.get('name')
    type = post_data.get('type')
    item_img = post_data.get('item_img')

    if name == None:
        return jsonify("Error: missing name")
    if item_img == None:
        return jsonify("Error: missing picture")

    new_record = Item(name, type, item_img)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(item_schema.dump(new_record))


@app.route('/item/add/multi', methods=["POST"])
def add_multi_items():
    if request.content_type != "application/json":
        return jsonify("ERROR: must be JSON")
    
    post_data = request.get_json()

    new_records = []

    for item in post_data:
        name = item.get('name')
        type = item.get('type')
        item_img = item.get('item_img')

        existing_item_check = db.session.query(Item).filter(item.name == name).first()
        if existing_item_check is None:
            new_record = item(name, type, item_img)
            db.session.add(new_record)
            db.session.commit()
            new_records.append(new_record)

        return jsonify(multi_item_schema.dump(new_records))


#GETS-----------------------------------------------------------------------------GETS

@app.route('/item/get', methods=["GET"])
def get_all_items():
    all_records = db.session.query(Item).all()
    return jsonify(multi_item_schema.dump(all_records))




@app.route('/item/get/<id>', methods=["GET"])
def get_item_id(id):
    one_item = db.session.query(Item).filter(Item.id == id).first()
    return jsonify(item_schema.dump(one_item))


#PUT---------------------------------------------------------------------------PUT
@app.route('/item/update/<id>', methods=["PUT"])
def update_item(id):
    if request.content_type != 'application/json':
        return jsonify("Error: must be JSON")

    put_data = request.get_json()
    name = put_data.get('name')
    type = put_data.get('type')
    item_img = put_data.get('item_img')

    item_to_update = db.session.query(Item).filter(Item.id == id).first()

    if name != None:
        item_to_update.name = name
    if type != None:
        item_to_update.type = type
    if item_img != None:
        item_to_update.item_img = item_img

    db.session.commit()

    return jsonify(item_schema.dump(item_to_update))


#DELETE------------------------------------------------------------------DELETE

@app.route('/item/delete/<id>', methods=["DELETE"])
def item_to_delete(id):
    delete_item = db.session.query(Item).filter(Item.id == id).first()
    db.session.delete(delete_item)
    db.session.commit()
    return jsonify("Deleted Successfully")

































if __name__ == "__main__":
    app.run(debug = True)