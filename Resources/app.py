import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify

## Database setup ##
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

## Flask setup ##
app = Flask(__name__)

# Initialize Flask routes
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()
    session.close()

    precipitation_dict = {}
    for date, prcp in results:
        precipitation_dict[date] = prcp
    
    #Return the JSON representation of your dictionary.
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperature():
    #Query the dates and temperature observations of the most active station for the last year of data.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= year_ago).filter(Measurement.station == 'USC00519281').all()

    session.close()

    station_observations = [{date:temp} for temp,date in results]

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    return(jsonify(station_observations))

@app.route("/api/v1.0/<start>")
def start_date_only(start):
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    sel = [
       func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    selected_start = session.query(*sel).\
    filter(Measurement.date >= start).all()
   
    session.close()

    #Return a JSON list of the min, max, and avg for the selected date.
    return(jsonify({start: selected_start[0]}))
    
@app.route("/api/v1.0/<start>/<end>")
def start_and_end_date(start, end):
    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    sel = [
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ]
    start_and_end = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    #Return a JSON list of the min, max, and avg between the selected start and end dates.
    return(jsonify(start_and_end))

if __name__ == "__main__":
    app.run(debug=True)