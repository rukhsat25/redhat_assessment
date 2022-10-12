''' imported libraries and modules'''

from crypt import methods
from flask import Flask
from flask import jsonify,request
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId

#creating the flask instance
app=Flask(__name__)

#connecting the MongoDB to the flask app
app.config['MONGO_URI']="mongodb://localhost:27017/pizza-house"
mongo=PyMongo(app)

#global counter variable for order_id
order_count=0


@app.route('/')
def home():
    return jsonify("HOME PAGE")

#routing app for welcome API
@app.route('/welcome',methods=['GET'])
def welcome():
    resp=jsonify("Welcome to Pizza House")
    resp.status_code=200
    return resp

#routing app for order API
@app.route('/order',methods=["POST"])
def order():
    _json=request.json
    _items=_json['order']
    global order_count
    order_count+=1
    mongo.db.orders.insert_one({'order':_items,"order_id":order_count})
    resp=jsonify(f"Order ID: {order_count}")
    resp.status_code=200
    return resp

#routing app for getorders API
@app.route('/getorders',methods=['GET'])
def get_orders():
    o=mongo.db.orders.find()
    return dumps(o)

#routing app for getorders/order_id API
@app.route('/getorders/<int:order_id>',methods=['GET'])
def get_orders_by_id(order_id):
    o=mongo.db.orders.find({"order_id":order_id})
    resp=dumps(o)
    if resp==dumps(o):
        return not_found()
    return resp

#error_handler if order_id does not exist
@app.errorhandler(404)
def not_found(error=None):
    message={
        'status':400,
        "message":'Not Found'
    }
    resp=jsonify(message)
    resp.status_code=404
    return resp


if __name__=="__main__":
    app.run(debug=True)
