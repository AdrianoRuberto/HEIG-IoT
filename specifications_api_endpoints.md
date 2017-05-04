#Specifications API endpoints

##Endpoints
- **/api/event** (unified datas from sensors via Pi)
- **/api/stats** (datas for frontend)
- **/api/occupation** (occupation in live)
- **/api/parktime** (time of car parking)
- **/api/inout** (Number of car entering or leaving the car park)

##/api/event
Post a new event to the system.  
A car entering (in) or leaving (out) the car park.

- **parking**		*int*
- **timestamp**		*int* (timestamp UTC Unix)
- **type**			*enum (in / out)*
- **id**			*string* (uniq ID of the vehicle)

##/api/stat
Get the dataset for the specified period, with the specified granularity.  
Returns how many vehicles are present in the car park for each sample.

- **parking**		*int*
- **granularity**	*enum (year / month / day / hour)*
- **from**			*int* (timestamp UTC Unix)
- **to**			*int* (timestamp UTC Unix)

##/api/occupation
Get the occupation of the car park in live.  
Returns how many vehicles are in the car park at a specific time.

- **parking**		*int*
- **time**			*int* (timestamp UTC Unix)

##/api/parktime
Get the mean parking time for a certain car, if specified, or for each car otherwise for a certain period.  
Return the mean parking time of a/each car for the specified period.

- **parking**		*int*
- **from**			*int* (timestamp UTC Unix)
- **to**			*int* (timestamp UTC Unix)
- **id**			*string* [optional] (uniq ID of the vehicle)

##/api/inout
Get the inputs and outputs for a certain car, if specified, or for each car otherwise for a certain period.  
Return the inputs and outputs of a/each car for the specified period.

- **parking**		*int*
- **from**			*int* (timestamp UTC Unix)
- **to**			*int* (timestamp UTC Unix)
- **id**			*string* [optional] (uniq ID of the vehicle)


###Usage:
####/api/event:

	{
		"parking" : 1
		"timestamp" : 1234567890
		"type" : "in"
		"id" : "acksbvakzsbvuasbvivrsvnavn"
	}

####/api/stat:

	{
		"parking" : 1
		"granularity" : "day"
		"from" : 1234567890
		"to" : 2234567890
	}

####/api/occupation:

	{
		"parking" : 1
		"time" : 1234567890
	}

####/api/parktime:

	{
		"parking" : 1
		"from" : 1234567890
		"to" : 2234567890
		"id" : "acksbvakzsbvuasbvivrsvnavn"
	}

####/api/inout:

	{
		"parking" : 1
		"from" : 1234567890
		"to" : 2234567890
	}