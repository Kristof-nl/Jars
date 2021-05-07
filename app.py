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
    jar_name = db.Column(db.String(50), unique=True)
    sort_operation = db.Column(db.String(50))
    amount = db.Column(db.Float)

    def __init__(self, jar_name, sort_operation, amount):
        self.jar_name = jar_name
        self.sort_operation = sort_operation
        self.amount = amount

#Operation schema
class OperationSchema(ma.Schema):
    class Meta:
        fields = ('id', 'jar_name', 'sort_operation', 'amount')

#Initialize schema
operation_schema = OperationSchema()
operations_schema = JarSchema(many=True)


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
    
    jar.amount = float(old_amount) + float(from_form['amount'])
    
    db.session.commit()

    return jar_schema.jsonify(jar)


if __name__ == '__main__':
    app.run(debug=True)
 