#Specifications API endpoints

##Endpoints
- **/api/event** (unified datas from sensors via Pi)
- **/api/stats** (datas for frontend)
- **/api/occupation** (occupation in live)
- **/api/parktime** (time of car parking)
- **/api/inout** (Number of car entering or leaving the car park)

##/api/event
Post a new event to the system. Defines which vehicle enters or leaves the car park.

- **timestamp**		*int*
- **type**			*enum (in / out)*
- **id**			*string* (uniq ID of the vehicle)

##/api/stats
Get the dataset for the specified period, with the specified granularity.
Returns how many vehicles are present in the car park for each sample.

- **granularity**	*enum (year / month / day / hour)*
- **from**			*int (timestamp UTC Unix)*
- **to**			*int (timestamp UTC Unix)*

##/api/occupationtime


- **granularity**	*enum (year / month / day / hour)*
- **from**			*int (timestamp UTC Unix)*
- **to**			*int (timestamp UTC Unix)*


###Usage:
####/api/event:

	{
		"timestamp" : 1234567890
		"type" : "in"
		"id" : "acksbvakzsbvuasbvivrsvnavn"
	}

####/api/stats:

	{
		"granularity" : "day"
		"from" : 1234567890
		"to" : 2234567890
	}
