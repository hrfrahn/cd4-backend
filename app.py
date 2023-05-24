from flask import Flask
import flask
import json
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/collision_years", methods = ["GET"])
def collision_years():
    print("years")
    filenames = os.listdir("crashes/")
    years = [w[0:4] for w in filenames]
    return flask.jsonify(years)

@app.route("/collisions/<year>", methods = ["GET"])
def collisions_year(year):
    print(year+" collisions data accessed")
    with open("crashes/"+year+"collisions.geojson", "r") as f:
        data = json.load(f)
        return flask.jsonify(data)

if __name__ == "__main__":
    app.run()