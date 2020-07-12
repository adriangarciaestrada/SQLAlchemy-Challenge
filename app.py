from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"<h4>Abailable APIs</h4>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/<start></br>"
        f"/api/v1.0/<start>/<end></br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    final_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    final_date_dt = datetime.date(int(str(final_date[0]).split('-')[0]),int(str(final_date[0]).split('-')[1]),int(str(final_date[0]).split('-')[2]))
    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= final_date_dt - datetime.timedelta(days=365)).all()
    precipitation = []
    for date, prcp in precip:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precipitation.append(precip_dict)
    return jsonify(precipitation)
    session.close()

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stat = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    stations = []
    for station, name, latitude, longitude, elevation in stat:
        stat_dict = {}
        stat_dict["station"] = station
        stat_dict["name"] = name
        stat_dict["latitude"] = latitude
        stat_dict["longitude"] = longitude
        stat_dict["elevation"] = elevation
        stations.append(stat_dict)
    return jsonify(stations)
    session.close()

@app.route("/api/v1.0/tobs")
def temperatures():
    session = Session(engine)
    final_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    active_stations = session.query(Measurement.station, func.count(Measurement.date)).group_by(Measurement.station).order_by(func.count(Measurement.date).desc()).all()
    print(final_date)
    final_date_dt = datetime.date(int(str(final_date[0]).split('-')[0]),int(str(final_date[0]).split('-')[1]),int(str(final_date[0]).split('-')[2]))
    temps = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station == active_stations[0][0]).filter(Measurement.date >= final_date_dt - datetime.timedelta(days=365)).all()
    temperatures = []
    for station, date, tobs in temps:
        temps_dict = {}
        temps_dict["station"] = station
        temps_dict["date"] = date
        temps_dict["tobs"] = tobs
        temperatures.append(temps_dict)
    return jsonify(temperatures)
    session.close()

@app.route("/api/v1.0/<start>")
def singleDate(start):
    session = Session(engine)
    try:
        datetime.datetime.strptime(start,'%Y-%m-%d')
    except ValueError:
        return jsonify({"error":f'This is not a supported date format, please use the format YYYY-MM-DD'})
    first_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()
    final_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    if start < first_date[0] or start > final_date[0]:
        return jsonify({'error':f'There are no reccords for the date {start}. The data goes from {first_date[0]} to {final_date[0]}'})
    else:
        info_dict = {}
        info_dict['TMIN']=session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).all()[0][0]
        info_dict['TMAX']=session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).all()[0][0]
        info_dict['TAVG']=round(session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()[0][0],2)
        return jsonify(info_dict)
    session.close()

@app.route("/api/v1.0/<start>/<end>")
def doubleDate(start,end):
    session = Session(engine)
    try:
        datetime.datetime.strptime(start,'%Y-%m-%d')
        datetime.datetime.strptime(end,'%Y-%m-%d')
    except ValueError:
        return jsonify({"error":f'This is not a supported date format, please use the format YYYY-MM-DD'})
    first_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()
    final_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    if start < first_date[0] or start > final_date[0]:
        return jsonify({'error':f'Your start date {start} is out of range. The data goes from {first_date[0]} to {final_date[0]}'})
    elif end < start:
        return jsonify({'error':f'Your start date {start} must be newer than your end date {end}'})
    elif end > final_date[0]:
        return jsonify({'error':f'Your end date {end} is out of range. The data goes from {first_date[0]} to {final_date[0]}'})
    else:
        info_dict = {}
        info_dict['TMIN']=session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).all()[0][0]
        info_dict['TMAX']=session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).all()[0][0]
        info_dict['TAVG']=round(session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()[0][0],2)
        return jsonify(info_dict)
    session.close()

if __name__ == "__main__":
    app.run(debug=True)