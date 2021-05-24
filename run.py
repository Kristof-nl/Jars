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
from models import Jar, Operation, jar_schema, jars_schema, operation_schema, operations_schema


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
    if Jar.query.get(id):
        jar = Jar.query.get(id)
        return jar_schema.jsonify(jar)
    else:
        return "Jar with this id doesn't exist."


#Update jar (both name and amount)
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
    if Jar.query.get(id):
        jar = Jar.query.get(id)

        db.session.delete(jar)
        db.session.commit()
        return f"Choosen jar id: {id} is deleted"

    else:
        return "Jar with this id doesn't exist."


#Add amount
@app.route('/jar/<id>/add', methods=['PUT'])
def add_to_jar(id):
    if Jar.query.get(id):
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
    else:
        return "Jar with this id doesn't exist."


#Withdraw amount
@app.route('/jar/<id>/withdraw', methods=['PUT'])
def withdraw_from_jar(id):
    if Jar.query.get(id):
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
    else:
        return "Jar with this id doesn't exist."


#Edit jar name
@app.route('/jar/<id>/edit/name', methods=['PUT'])
def edit_jar_name(id):
    if Jar.query.get(id):
        jar = Jar.query.get(id)
        from_form = request.form
        jar.name = from_form['name']
        
        db.session.commit()

        return jar_schema.jsonify(jar)
    else:
        return "Jar with this id doesn't exist."


#Edit amount
@app.route('/jar/<id>/edit/amount', methods=['PUT'])
def edit_jar_amount(id):
    if Jar.query.get(id):
        jar = Jar.query.get(id)

        from_form = request.form
        jar.amount = from_form['amount']
        
        db.session.commit()

        return jar_schema.jsonify(jar)
    else:  
        return "Jar with this id doesn't exist."


#Currency
@app.route('/jar/<id>/<currency>', methods=['GET'])
def currency(id, currency):
    if Jar.query.get(id):
        jar = Jar.query.get(id)
        if currency == "euro":
            jar.amount = jar.amount * 0.22
        elif currency == "USD":
            jar.amount = jar.amount * 0.26
        elif currency == "GBP":
            jar.amount = jar.amount * 0.19
        else:
            return "Unknown currency."

        return jar_schema.jsonify(jar)
    else:  
        return "Jar with this id doesn't exist."

#Transfer
@app.route('/jar/<id1>/<id2>/tr', methods=['PUT'])
def transfer(id1,id2):
    #Transfer operation
    if Jar.query.get(id1) and Jar.query.get(id2):
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
    else:
        if not Jar.query.get(id1) and Jar.query.get(id2):
            return f"Jar with id {id1} doesn't exist."
        elif Jar.query.get(id1) and not Jar.query.get(id2):
            return f"Jar with id {id2} doesn't exist."
        else:
            return "There aren't jars with this id's."

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

    db.session.add(new_operation1, new_operation2)
    db.session.commit()

    return operation_schema.jsonify(new_operation1)


#Get transaction
@app.route('/jar/transaction/<id>', methods=['GET'])
def get_transaction(id):
    if Operation.query.get(id):
        transaction = Operation.query.get(id)

        return operation_schema.jsonify(transaction)
    else:
        return "There isn't a transaction with this id."


#Get all transactions
@app.route('/jar/transactions', methods=['GET'])
def get_transactions():
    all_transactions = Operation.query.all()
    result = operations_schema.dump(all_transactions)

    return jsonify(result)


#Get all transactions for specific jar
@app.route('/jar/transaction/jar/<id>', methods=['GET'])
def get_jar_transactions(id):
    all_transactions = Operation.query.all()
    result = operations_schema.dump(all_transactions)

    #Get only transactions with specific jar_id
    result_id = (list(filter(lambda x:x["jar_id"]== int(id), result)))
    if result_id:
        return jsonify(result_id)
    else:
        return "There isn't a jar with this id."


if __name__ == '__main__':
    app.run(debug=True)
 