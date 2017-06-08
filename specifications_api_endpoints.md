#Specifications API endpoints

##Endpoints
- **/api/event** (unified data from sensors via Pi)
- **/api/stats** (data for frontend)
- **/api/occupation** (occupation in live)
- **/api/parktime** (time of car parking)
- **/api/inout** (Number of car entering or leaving the car park)

##/api/event
Post a new event to the system.  
A car entering (in) or leaving (out) the car park.

- **parking**		*int*
- **timestamp**		*int* (timestamp UTC Unix in ms)
- **device**		*enum (mlx / wifi / flir)* (device type)
- **type**			*enum (in / out)*
- **id**			*string* [optional] (unique ID of the vehicle)

##/api/stat
Get the dataset for the specified period, with the specified granularity.  
Returns how many vehicles are present in the car park for each sample (mean).

- **parking**		*int*
- **granularity**	*enum (year / month / day / hour)*
- **from**			*int* (timestamp UTC Unix)
- **to**			*int* (timestamp UTC Unix)

##/api/occupation
Get the occupation of the car park in live.  
Returns how many vehicles are in the car park at a specific time.

- **parking**		*int*

##/api/vehicule
Get the list of vehicules that was present during the specified period.  
Return a list of vehicules.

- **parking**		*int*
- **from**			*int* (timestamp UTC Unix)
- **to**			*int* (timestamp UTC Unix)

##/api/parktime/\<id\>
Get the mean parking time for a certain car otherwise for a certain period.
Return the mean parking time of a car for the specified period.

- **parking**		*int*
- **granularity**	*enum (year / month / day / hour)*
- **from**			*int* (timestamp UTC Unix)
- **to**			*int* (timestamp UTC Unix)
- **id**			*string* (unique ID of the vehicle)

##/api/inout/\<id\>
Get the inputs and outputs for a certain car for a certain period.
Return the inputs and outputs of a car for the specified period.

- **parking**		*int*
- **granularity**	*enum (year / month / day / hour)*
- **from**			*int* (timestamp UTC Unix)
- **to**			*int* (timestamp UTC Unix)
- **id**			*string* (unique ID of the vehicle)


###Usage:
####/api/event: (request)

	{
		"parking" : 1,
		"timestamp" : 1234567890,
		"device" : "mlx",
		"type" : "in",
		"id" : "1f1a4ea7c9e0d6ca"
	}

####/api/stat: (response)

	{
		[
			{
				"from" : 1234567000,
				"vehicule" : 105
			},
			{
				"from" : 1234568000,
				"vehicule" : 138
			},
			{
				"from" : 1234569000,
				"vehicule" : 147
			},
			{
				"from" : 1234570000,
				"vehicule" : 151
			},
			{
				"from" : 1234571000,
				"vehicule" : 169
			},
			{
				"from" : 1234572000,
				"vehicule" : 173
			},
			{
				"from" : 1234573000,
				"vehicule" : 180
			}
		]
	}

####/api/occupation: (response)

	{
		"vehicule" : 146
	}

####/api/parktime/1f1a4ea7c9e0d6ca: (response)

	{
		[
			{
				"from" : 1234567000,
				"mean" : 0000007658
			},
			{
				"from" : 1234568000,
				"mean" : 0000007658
			},
			{
				"from" : 1234569000,
				"mean" : 0000007658
			}
		]
	}

####/api/inout/1f1a4ea7c9e0d6ca: (response)

	{
		[
			{
				"from" : 1234567000,
				"in" : 20,
				"out" : 20
			},
			{
				"from" : 1234568000,
				"in" : 10,
				"out" : 10
			},
			{
				"from" : 1234569000,
				"in" : 13,
				"out" : 12
			}
		]
	}