# Schedule

This is a simple program to parse schedules exported from TimeEdit, do simple filtering on them and export them to a Google calendar. Feel free to change to output format to Outlook instead, or change the way it outputs to a calendar.

# Example

Say for example that you are taking the course tsrt12 and are in a certain lesson group, and will only participate in certain labs.
You only want to see the ones your attending.
The following code will produce the desired schedule:

```py
from datetime import datetime
from schedule import Schedule

tsrt12 = Schedule.from_csv('TSRT12')

tsrt12 = tsrt12.within(undervisningstyp='Lektion').keep(fria_grupper='A')
tsrt12 = tsrt12.within(information='Lab2').keep(startdatum=datetime(2021, 2, 25))
tsrt12 = tsrt12.within(information='Lab3').keep(startdatum=datetime(2021, 3, 8))

tsrt12.to_csv('tsrt12-schedule')
```

The program will expose four simple functions to use: `from_csv()`, `to_csv()`, `within()` and `keep()`.
It will convert all input fields in the csv to lowercase and convert all spaces into underscores, as seen on line 6.
