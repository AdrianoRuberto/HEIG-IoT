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


r = range(600*24)
dstat = process_day(r)
print(dstat)

mstat = process_month(dstat)
print(mstat)

ystat = process_year(dstat)
print(ystat)
