
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
import datetime as dt

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)
# Reflect an existing database into new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

#Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from python to the DB
session = Session(engine)

#Flask Setup
app = Flask(__name__)

#Flask Routes
@app.route("/")
def welcome():
    return( 
        f"Welcome to Surf's Up! - Hawaii's Climate API<br/>"
        f"Available Routes:<br/>"
        f"Precipitation Data /api/v1.0/precipitaton<br/>"
        f"Station Data /api/v1.0/stations<br/>"
        f"Temperature Yearly Data /api/v1.0/tobs<br/>"
        f"MIN/AVG/MAX Temperature Timeline Data<br/>"
        f"Start Date: /api/v1.0/<start><br/>"
        f"End Date: /api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitaton")
def precipitaton():
    """Returns a list of precipitations from last year"""
    # Query dates ordered by descending and retreiving the end date value
    end_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    end_date = end_date[0]

    ##Calculating the date 1 year ago from today
    year_ago = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days=366)

    #Query to retreive the data and precipitation scores
    results_precipitation = session.query(measurement.date, measurement.prcp)\
        .filter(measurement.date >= year_ago).all()

    #Convert list of tuples into normal list
    precipitation_dict = dict(results_precipitation)

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    station_data = session.query(measurement.station).group_by(measurement.station).all()
    #Converting list o ftuples into normal list
    stations_list = list(np.ravel(station_data))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    end_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    end_date = end_date[0]

    year_ago = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days=366)

    results_tobs = session.query(measurement.date, measurement.tobs)\
        .filter(measurement.date >= year_ago).all()

    tobs_list = list(results_tobs)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start=None):
    from_start = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
    .filter(measurement.date >= start)\
    .group_by(measurement.date).all()

    from_start_list = list(from_start)
    return jsonify(from_start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    between_dates = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
    .filter(measurement.date >= start)\
    .filter(measurement.date <= end)\
    .group_by(measurement.date).all()

    between_date_list = list(between_dates)
    return jsonify(between_date_list)


if __name__ == '__main__':
    app.run(debug=True)