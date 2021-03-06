from __main__ import db, app
from flask_marshmallow import Marshmallow
import datetime


#initialize Marshmallow
ma = Marshmallow(app)

#Jar class model
class Jar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    amount = db.Column(db.Float)
    create_time = db.Column(db.DATETIME)
    

    def __init__(self, name, amount, create_time):
        self.name = name
        self.amount = amount
        self.create_time = create_time

#Jar schema
class JarSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'amount', 'create_time')


#Initialize schema
jar_schema = JarSchema()
jars_schema = JarSchema(many=True)


#Operation class model
class Operation(db.Model):
    operation_id = db.Column(db.Integer, primary_key=True)
    jar_id = db.Column(db.Integer)
    sort_operation = db.Column(db.String(100))
    operation_time = db.Column(db.DATETIME)

    def __init__(self, jar_id, sort_operation, operation_time):
        self.jar_id = jar_id
        self.sort_operation = sort_operation
        self.operation_time = operation_time


#Operation schema
class OperationSchema(ma.Schema):
    class Meta:
        fields = ('operation_id', 'jar_id', 'sort_operation', 'operation_time')

#Initialize schema
operation_schema = OperationSchema()
operations_schema = OperationSchema(many=True)