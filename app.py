from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)

#Create datebase
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

@app.route('/', methods = ['GET'])
def get():
    return jsonify({ 'msg' : 'Madzia kocha Krzysia'})

if __name__ == '__main__':
    app.run(debug=True)