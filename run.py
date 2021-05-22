from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

import os, json

app = Flask(__name__)

#Create and initialize datebase
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#To avoid circular import
from models import Jar, Operation


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

    #Save operation
    sort_operation = f"Add {float(from_form['amount'])}. Balance after this operation: {jar.amount}"
    jar_id = id
    new_operation = Operation(jar_id, sort_operation)
    
    db.session.add(new_operation)
    db.session.commit()

    return operation_schema.jsonify(new_operation)

#Withdraw amount
@app.route('/jar/<id>/withdraw', methods=['PUT'])
def withdraw_from_jar(id):
    jar = Jar.query.get(id)
    old_amount = jar.amount
    from_form = request.form
    if float(from_form['amount']) > old_amount:
        return "Not enough money for this transaction"
    else:
        jar.amount = float(old_amount) - float(from_form['amount'])

    #Save operation
    sort_operation = f"Withdraw {float(from_form['amount'])}. Balance after this operation: {jar.amount}"
    jar_id = id
    new_operation = Operation(jar_id, sort_operation)
    
    db.session.add(new_operation)
    db.session.commit()

    return operation_schema.jsonify(new_operation)

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
    new_amount_jar1 = jar1.amount
    new_amount_jar2 = jar2.amount
    #Separate it in 2 transaction add for jar1 and withdraw for jar2
    jar_id1 = id1
    sort_operation1 = f"Transfer(add) {float(from_form['amount'])} from jar_id{id2}. Balance after this operation: {new_amount_jar1}."
    jar_id2 = id2
    sort_operation2 = f"Transfer(withdraw) {float(from_form['amount'])} to jar_id{id1}. Balance after this operation: {new_amount_jar2}."

    new_operation1 = Operation(jar_id1, sort_operation1)
    new_operation2 = Operation(jar_id2, sort_operation2)

    db.session.add(new_operation1)
    db.session.add(new_operation2)
    db.session.commit()

    return operation_schema.jsonify(new_operation1)


#Get transaction
@app.route('/jar/transaction/<id>', methods=['GET'])
def get_transaction(id):
    transaction = Operation.query.get(id)

    return operation_schema.jsonify(transaction)


#Get all transactions
@app.route('/jar/transactions', methods=['GET'])
def get_transactions():
    all_transactions = Operation.query.all()
    result = operations_schema.dump(all_transactions)

    return jsonify(result)


#Get all transactions for specific jar
@app.route('/jar/transactions/<id>', methods=['GET'])
def get_jar_transactions(id):
    all_transactions = Operation.query.all()
    result = operations_schema.dump(all_transactions)

    #Get only transactions with specific id
    result_id = (list(filter(lambda x:x["jar_id"]== int(id), result)))
    

    return jsonify(result_id)


if __name__ == '__main__':
    app.run(debug=True)
 