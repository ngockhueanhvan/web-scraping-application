from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
import scrape_data

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/events_db"
mongo = PyMongo(app)

@app.route("/")
def index():
    this_weekend = mongo.db.this_weekend.find_one()
    return render_template("index.html", this_weekend=this_weekend)


@app.route("/scrape")
def scrape():
    this_weekend = mongo.db.this_weekend
    data = scrape_data.scrape_all()
    this_weekend.update({}, data, upsert=True)
    return redirect('/', code=302)


if __name__ == "__main__":
    app.run()
