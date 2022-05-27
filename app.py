from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
#import os

app = Flask(__name__)
CORS(app)

#basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://ppxwlwmezjrlbd:86c43d53b0d52918556d627900d584f1ac8b1e00db95f1279f146c1a831f3965@ec2-34-230-153-41.compute-1.amazonaws.com:5432/d3o8uqsrg761b7"


db = SQLAlchemy(app)
ma = Marshmallow(app)

class Surfboard(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String)
    item_img = db.Column(db.String, unique=True)

    def __init__(self, name, type, item_img):
        self.name = name
        self.type = type
        self.item_img = item_img

#SCHEMAS---------------------------------------------------SCHEMAS

class SurfboardSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'type', 'item_img')

surfboard_schema = SurfboardSchema()
multi_surfboard_schema = SurfboardSchema(many=True)

#POSTS-------------------------------------------------------POSTS

@app.route('/surfboard/add', methods=["POST"])
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

    new_record = Surfboard(name, type, item_img)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(surfboard_schema.dump(new_record))


@app.route('/surfboard/add/multi', methods=["POST"])
def add_multi_surfboard():
    if request.content_type != "application/json":
        return jsonify("ERROR: must be JSON")
    
    post_data = request.get_json()

    new_records = []

    for surfboard in post_data:
        name = surfboard.get('name')
        type = surfboard.get('type')
        item_img = surfboard.get('item_img')

        existing_surfboard_check = db.session.query(Surfboard).filter(surfboard.name == name).first()
        if existing_surfboard_check is None:
            new_record = surfboard(name, type, item_img)
            db.session.add(new_record)
            db.session.commit()
            new_records.append(new_record)

        return jsonify(multi_surfboard_schema.dump(new_records))


#GETS-----------------------------------------------------------------------------GETS

@app.route('/surfboard/get', methods=["GET"])
def get_all_surfboard():
    all_records = db.session.query(Surfboard).all()
    return jsonify(multi_surfboard_schema.dump(all_records))




@app.route('/surfboard/get/<id>', methods=["GET"])
def get_surfboard_id(id):
    one_surfboard= db.session.query(Surfboard).filter(Surfboard.id == id).first()
    return jsonify(surfboard_schema.dump(one_surfboard))


#PUT---------------------------------------------------------------------------PUT
@app.route('/surfboard/update/<id>', methods=["PUT"])
def update_surfboard(id):
    if request.content_type != 'application/json':
        return jsonify("Error: must be JSON")

    put_data = request.get_json()
    name = put_data.get('name')
    type = put_data.get('type')
    item_img = put_data.get('item_img')

    surfboard_to_update = db.session.query(Surfboard).filter(Surfboard.id == id).first()

    if name != None:
        surfboard_to_update.name = name
    if type != None:
        surfboard_to_update.type = type
    if item_img != None:
        surfboard_to_update.item_img = item_img

    db.session.commit()

    return jsonify(surfboard_schema.dump(surfboard_to_update))


#DELETE------------------------------------------------------------------DELETE

@app.route('/surfboard/delete/<id>', methods=["DELETE"])
def surfboard_to_delete(id):
    delete_surfboard = db.session.query(Surfboard).filter(Surfboard.id == id).first()
    db.session.delete(delete_surfboard)
    db.session.commit()
    return jsonify("Deleted Successfully")


































if __name__ == "__main__":
    app.run(debug = True)