from flask import Flask, request, jsonify
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


#Create a jar
@app.route('/jar', methods=['POST'])
def add_jar():
    name = request.json['name']
    amount = request.json['amount']

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



if __name__ == '__main__':
    app.run(debug=True)
 