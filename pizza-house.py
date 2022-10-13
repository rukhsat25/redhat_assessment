''' imported libraries and modules'''

from crypt import methods
from flask import Flask
from flask import jsonify,request,make_response
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
import pika

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
    resp=jsonify("Welcome to Pizza House","status : 200")
    return resp

#routing app for enqueue message API
connection_parameters=pika.ConnectionParameters('localhost')
connection=pika.BlockingConnection(connection_parameters)
channel=connection.channel()
channel.queue_declare(queue="letterbox")
@app.route('/order/enqueue',methods=["POST"])
def order_enqueue():
    _json=request.json
    message=_json['order']
    channel.basic_publish(exchange="",routing_key="letterbox",body=message)
    return jsonify("Order Enqueue Successfully"," status : 200")

#routing app for dequeue message API
@app.route('/order/dequeue',methods=["GET"])
def order_dequeue():
    def message_received(ch,method,properties,body):
        global order_count
        order_count+=1
        mongo.db.orders.insert_one({'order':body,"order_id":order_count})
        resp=jsonify(f"Order ID: {order_count}","status : 200")
        return resp
    channel.basic_consume(queue="letterbox",auto_ack=False,on_message_callback=message_received)
    channel.start_consuming()


#routing app for order API
@app.route('/order',methods=["POST"])
def order():
    _json=request.json
    _items=_json['order']
    global order_count
    order_count+=1
    mongo.db.orders.insert_one({'order':_items,"order_id":order_count})
    resp=jsonify(f"Order ID: {order_count}","status : 201")
    return resp

#routing app for getorders API
@app.route('/getorders',methods=['GET'])
def get_orders():
    o=mongo.db.orders.find()
    return make_response(dumps(o),200)

#routing app for getorders/order_id API
@app.route('/getorders/<int:order_id>',methods=['GET'])
def get_orders_by_id(order_id):
    o=mongo.db.orders.find({"order_id":order_id})
    resp=dumps(o)
    if resp==dumps(o):
        return not_found()
    return make_response(resp,200)

#error_handler
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
