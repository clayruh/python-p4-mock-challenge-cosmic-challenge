#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.get('/planets')
def get_planets():
    planets = Planet.query.all()
    # can add rules within the get request
    response = [planet.to_dict(rules=("-missions",)) for planet in planets]
    return jsonify(response), 200

@app.get('/planets/<int:id>')
def planet_by_id(id):
    try:
        planet = Planet.query.filter(Planet.id == id).first()
        response = planet.to_dict()
        return jsonify(response), 201
    except AttributeError:
        return jsonify({"error": "No planet found"}), 404

@app.get('/scientists')
def get_scientists():
    scientists = Scientist.query.all()
    response = [scientist.to_dict(rules=('-missions',)) for scientist in scientists]
    return jsonify(response), 200

@app.get('/scientists/<int:id>')
def get_scientist_by_id(id):
    try:
        scientist = Scientist.query.filter(Scientist.id == id).first()
        return jsonify(scientist.to_dict()), 200
    except AttributeError:
        return jsonify({"error": "No scientist found"}), 404
    
@app.post('/scientists')
def create_scientist():
    data = request.json
    print(data)
    try: 
        # can use scientist = Scientist(**data)
        scientist = Scientist(name=data['name'], field_of_study=['field_of_study'])
        db.session.add(scientist)
        db.session.commit()
        return jsonify(scientist.to_dict()), 201
    except KeyError: 
        return {"error": ["validation errors"]}, 406
    
@app.patch('/scientists/<int:id>')
def update_scientist(id):
    try: 
        data = request.json
        Scientist.query.filter(Scientist.id == id).update(data)
        db.session.commit()
        scientist = Scientist.query.filter(Scientist.id == id).first()
        return jsonify(scientist.to_dict()), 202
    except:
        return jsonify({"error": "Invalid data"}), 406

@app.delete('/scientists/<int:id>')
def delete_scientist(id):
    try: 
        scientist = Scientist.query.filter(Scientist.id == id).first()
        db.session.delete(scientist)
        db.session.commit()
        return {}, 204
    except:
        return jsonify({"error": "That scientist doesn't exist bc you deleted him..."}), 404

@app.post('/missions')
def create_mission():
    try: 
        data = request.json
        planet = Planet.query.filter(Planet.id == data['planet_id']).first()
        scientist = Scientist.query.filter(Scientist.id == data['scientist_id']).first()
        mission = Mission(name=data["name"], scientist=scientist, planet=planet)
        db.session.add(mission)
        db.session.commit()
        return jsonify(mission.to_dict()), 201
    except:
        return jsonify({"error": "invalid data submitted"}), 404

if __name__ == '__main__':
    app.run(port=5555, debug=True)
