# Objective

Write a crawler for BoltBus that can extract:
* list of stops
* list of routes
* list of departures

## Step 1: get stops

This process is done once to create a mapping between their stops and ours.

From this [page](http://bit.ly/1mbczAX), get the list of all bus stops including the address, latitude and longitude.  The output should be stored in a `stops.json` and the schema should be something like this:

```json
[
	{
		"stop_name": "New York W 33rd St & 11-12th Ave (DC,BAL,BOS,PHL)",
		"stop_location":"611 W. 33rd Street, New York, NY, 10001",
		"lat":40.755661,
		"long":-74.00337
	}
]
```

The step should be invoked like so

```sh
python run.py --extract stops --output stops.json
```

## Step 2: get routes

This process is done once to get the list of all possible routes with departures from this operator.

From this [page](http://bit.ly/1mbczAX), get the list of all possible routes, i.e., all valid stop pairings.  The output should stored in `routes.json` and the schema should be something like this:

```json
[
	{
		"origin": "New York W 33rd St & 11-12th Ave (DC,BAL,BOS,PHL)",
		"destination":"Boston South Station - Gate 9 NYC-Gate 10 NWK/PHL",
	},
	{
		"origin": "New York 1st Ave Between 38th & 39th (To BOS)",
		"destination":"Boston South Station - Gate 9 NYC-Gate 10 NWK/PHL",
	}
]
```

The step should be invoked like so

```sh
python run.py --extract routes --output routes.json
```


## Step 3: get departures

This process is done repeatedly to update our database of departure. As an input, this function should accept an origin, destination and a range of dates for which departures will be returned.

1. Go to this [page](http://bit.ly/1hXalGT)
1. For each route in the list generated in step 2, get the list of all one-way departures for one passenger.
1. For each departure extract the following information:

	* departure time
	* arrival time
	* duration
	* adult one-way price

The output should be stored in `departures.json` and the schema should look something like this:

```json
[
	{
		"origin": "New York 1st Ave Between 38th & 39th (To BOS)",
		"destination": "Boston South Station - Gate 9 NYC-Gate 10 NWK/PHL",
		"departure_time": "2014-05-01T18:30:00",
		"arrival_time": "2014-05-01T22:45:00",
		"duration": "4:15",
		"price": 23.00
	}
]
```

The step should be invoked like so

```sh
python run.py --extract departures --output departures.json --startdate 2013-11-13 --enddate 2013-11-20
```

# Non-functional requirements

* the code should be written in Python and compatible with Python 2.7.
* the code should be hosted on github, and the repo should be shared with Busbud
* the code should be written in a way that it can easily be extended to become a scheduled process that updates our
database of departure
* any packages required must be installable via `pip install -r requirements.txt`, see [pip](http://www.pip-installer.org/en/latest/)
