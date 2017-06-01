# Returns the delta of in/out for a vehicle with the correct granularity
def process_inout(data, granularity):
    # by hour
    list_hour = []
    for row in data:
        delta = row['timestamp'] % 3600
        hour = row['timestamp'] - delta

        if row['type'] == 'in':
            list_hour[hour] += 1
        else:
            list_hour[hour] -= 1

    # take granularity and compress the list (hours are maybe not in order and not all hours are present)

    if granularity not in {'day', 'month', 'year'}:
        return list_hour

    # by day
    list_day = []
    for key in list_hour:
        delta = key % 3600 * 24
        day = key - delta

        list_day[day] += list_hour[key]

    if granularity == 'month':
        # by month
        list_month = []
        for key in list_day:
            delta = key % 3600 * 24 * 30
            month = key - delta

            list_month[month] += list_day[key]

        return list_month
    elif granularity == 'month':
        # by year
        list_year = []
        for key in list_day:
            delta = key % 3600 * 24 * 365
            year = key - delta

            list_year[year] += list_day[key]

        return list_year
    else:
        return list_day


def process_day(data):
    hours = sorted(data)  # make lambda to filter on object->timestamp instead of object

    fulldays = [hours[x:x + 24] for x in range(0, len(hours), 24)]
    dayshours = []

    for d in fulldays:
        dayshours.append(d[6:19])

    days = []
    for d in dayshours:
        days.append(sum(d) / len(d))

    return days


def process_month(days):
    monthdays = [days[x:x + 30] for x in range(0, len(days), 30)]

    months = []
    for m in monthdays:
        months.append(sum(m) / len(m))

    return months


def process_year(days):
    yeardays = [days[x:x + 365] for x in range(0, len(days), 365)]

    years = []
    for y in yeardays:
        years.append(sum(y) / len(y))

    return years


# Tests
r = range(600 * 24)
dstat = process_day(r)
print(dstat)

mstat = process_month(dstat)
print(mstat)

ystat = process_year(dstat)
print(ystat)
