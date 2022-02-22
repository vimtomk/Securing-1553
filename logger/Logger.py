# This file attempts to listen in on the communications of the MIL Bus and log activity in a .json file

# This file is a WORK IN PROGRESS
# ToDo:
# - Replace example event with actual code that gets an event from the simulator
# - Loop execution so the logging occurs continuously as long as the program is left running

import json
from datetime import datetime

# Function to add date and time information to a log entry
def addtime ( dictionary ) :
    "This takes a dictionary and adds entries for the date and time of function call"
    now = datetime.now()
    dictionary['time_year'] = now.strftime('%Y')
    dictionary['time_month'] = now.strftime('%m')
    dictionary['time_day'] = now.strftime('%d')
    dictionary['time_hour'] = now.strftime('%H')
    dictionary['time_minute'] = now.strftime('%M')
    dictionary['time_second'] = now.strftime('%S')
    return

# Example dict of event to log
event = {
    'flag1' : '01',
    'flag2' : '11',
    'length' : '07'
}
# Add time data
addtime(event)

# Name of file should be from date
now = datetime.now()
jsonfilename = now.strftime('%m-%d-%Y_log.json')


# Output of event to json
with open(jsonfilename, 'a') as event_dumped :
    json.dump(event, event_dumped)