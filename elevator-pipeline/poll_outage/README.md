# Poll MTA Escalator and Elevator Outages

Quick python script to poll the MTA escalator & elevator outage API described [here](http://web.mta.info/developers/resources/nyct/EES/ElevEscDefinitions.pdf)

Raw XML can be viewed [here](http://localhost:5002/api/Person/59e11783add6ed001f3901cf?limit=20)

Script is currently running on AWS VM once every 12 hours and results are stored in a sqlite db. This work is incomplete but it's best to start collecting raw data as soon as possible. A true ETL script will be required to dedupe and structure the data.

To run script 
Activate python [virtual env](https://docs.python.org/3/library/venv.html)
```
pip install -r requirements.txt
python poll.py
```

Tested with Python 3.6.1
