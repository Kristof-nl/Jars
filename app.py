from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)

#Create and initialize datebase
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#initialize Marshmallow
ma = Marshmallow(app)

#Jar class model
class Jar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    amount = db.Column(db.Float)
    

    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

#Jar schema
class JarSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'amount')


#Initialize schema
jar_schema = JarSchema()
jars_schema = JarSchema(many=True)


#Operation class model
class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sort_operation = db.Column(db.String(100))

    def __init__(self, sort_operation):
        self.sort_operation = sort_operation

#Operation schema
class OperationSchema(ma.Schema):
    class Meta:
        fields = ('id','sort_operation')

#Initialize schema
operation_schema = OperationSchema()
operations_schema = OperationSchema(many=True)


#Create a jar
@app.route('/jar', methods=['POST'])
def add_jar():
    name = request.json['name']
    amount = request.json['amount']
    if amount < 0:
        return "Amount can't be smaller than 0"
    else:
        new_jar = Jar(name, amount)

        db.session.add(new_jar)
        db.session.commit()

        return jar_schema.jsonify(new_jar)


#Get all jars
@app.route('/jar', methods=['GET'])
def get_jars():
    all_jars = Jar.query.all()
    result = jars_schema.dump(all_jars)

    return jsonify(result)

#Get single jar
@app.route('/jar/<id>', methods=['GET'])
def get_jar(id):
    jar = Jar.query.get(id)

    return jar_schema.jsonify(jar)

#Update jar
@app.route('/jar/<id>', methods=['PUT'])
def update_jar(id):
    jar = Jar.query.get(id)

    name = request.json['name']
    amount = request.json['amount']

    jar.name = name
    jar.amount = amount

    db.session.commit()

    return jar_schema.jsonify(jar)


#Delete jar
@app.route('/jar/<id>', methods=['DELETE'])
def delete_jar(id):
    jar = Jar.query.get(id)

    db.session.delete(jar)
    db.session.commit()

    return f"Choosen jar id: {id} is deleted"

#Add amount
@app.route('/jar/<id>/add', methods=['PUT'])
def add_to_jar(id):
    jar = Jar.query.get(id)
    old_amount = jar.amount
    from_form = request.form
    if float(from_form['amount']) <= 0:
        return "Amount must be bigger than 0"
    else:
        jar.amount = float(old_amount) + float(from_form['amount'])
    
    db.session.commit()

    return jar_schema.jsonify(jar)

#Edit jar name
@app.route('/jar/<id>/edit', methods=['PUT'])
def edit_jar_name(id):
    jar = Jar.query.get(id)
    old_name = jar.name
    from_form = request.form
    
    jar.name = from_form['name']
    
    db.session.commit()

    return jar_schema.jsonify(jar)


#Currency
@app.route('/jar/<id>/<currency>', methods=['GET'])
def ero(id, currency):
    jar = Jar.query.get(id)
    if currency == "euro":
        jar.amount = jar.amount * 0.22
    elif currency == "USD":
         jar.amount = jar.amount * 0.26
    elif currency == "GBP":
         jar.amount = jar.amount * 0.19

    return jar_schema.jsonify(jar)


#Transfer
@app.route('/jar/<id1>/<id2>/tr', methods=['PUT'])
def transfer(id1,id2):
    #Transfer operation
    jar1 = Jar.query.get(id1)
    jar2 = Jar.query.get(id2)
    old_amount1 = jar1.amount
    old_amount2 = jar2.amount
    from_form = request.form
    if float(from_form['amount']) <= 0:
        return "Amount must be bigger than 0"
    else:
        if float(from_form['amount']) <= float(old_amount2):
            jar1.amount = float(old_amount1) + float(from_form['amount'])
            jar2.amount = float(old_amount2) - float(from_form['amount'])
        else:
            return f"Not enough money in jar with id{id2} for this opperation"

    #Save transaction
    jar1_id = jar1.id
    jar2_id = jar2.id
    new_amount_jar1 = jar1.amount
    new_amount_jar2 = jar2.amount
    sort_operation = f"Transfer {float(from_form['amount'])} from jar_id{id2} to jar_id{id1}"
    new_operation = Operation(sort_operation)
    

    db.session.add(new_operation)
    
    
    db.session.commit()

    return operation_schema.jsonify(new_operation)


if __name__ == '__main__':
    app.run(debug=True)
 