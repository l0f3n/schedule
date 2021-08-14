import csv
from datetime import datetime

VERBOSE = True

class Schedule:
    """ A schedule containg Events.
    
    When iterating over events, they are ordered by date.
    """

    def __init__(self, schedule=None, name="A schedule"):
        self.name = name
        self.schedule = schedule or []
        self.__inner_filter = [True for _ in range(len(self))]

        assert all(isinstance(event, Event) for event in self), "All events should be of type Event."

    def __str__(self):
        return f'schedule \'{self.name}\' with {len(self)} events'

    def __len__(self):
        return len(self.schedule)

    def __iter__(self):
        return (event for event in self.schedule)

    @staticmethod
    def from_csv(filename):
        """ Reads a schedule exported from TimeEdit in csv format from '<filename>.csv' and returns 
        it as a new Schedule. """
        with open(f'{filename}.csv', newline='', encoding='utf-8') as f:
            for _ in range(3):
                next(f)
            
            sched = Schedule([Event(event_data) for event_data in list(csv.DictReader(f))], name=filename)
        
        if VERBOSE:
            print(f"Read {sched} from '{filename}.csv'")

        return sched

    def within(self, **kwargs):
        """ Specifies which events a subsequent call to keep should affect.

        If multiple kwargs are sent, an event matching ANY filter will
        be affected. Multiple calls to this function will respect previous calls, 
        meaning calling this multiple times will affect events matching ALL
        filters. """
        self.__inner_filter = [self.__inner_filter[index] and any(value == getattr(event, key) if key in Event.exact_matches else value in getattr(event, key) for key, value in kwargs.items()) for index, event in enumerate(self.schedule)]
        return self

    def keep(self, **kwargs):
        """ Returns a new schedule with the events matching ALL filters. """
        matches = [all(value == getattr(event, key) if key in Event.exact_matches else value in getattr(event, key) for key, value in kwargs.items()) if len(kwargs) > 0 else True for event in self.schedule]

        sched = Schedule([event for index, event in enumerate(self.schedule) if not self.__inner_filter[index] or matches[index]], name=self.name)
        
        self.__inner_filter = [True for _ in range(len(sched))]

        if VERBOSE:
            print(f'Filtered {self} to {len(sched)} events')

        return sched

    def to_csv(self, filename):
        """ Writes a csv for the current schedule in a format that Google
        Calendar accepts to '<filename>.csv'. """
        if len(self) <= 0:
            return

        with open(f'{filename}.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Subject', 'Start Date', 'All Day Event', 'Start Time', 'End Time', 'Location', 'Description'])
            writer.writeheader()
            writer.writerows([event.to_dict() for event in self])

        if VERBOSE:
            print(f"Wrote schedule '{self.name}' to '{filename}.csv'")


class Event:
    """ An Event. """

    exact_matches = set(['startdatum', 'slutdatum', 'starttid', 'sluttid'])

    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key.lower().strip().replace(' ', '_'), value)
                
        self.startdatum = datetime.strptime(data['Startdatum'], r'%Y-%m-%d')
        self.starttid = datetime.strptime(data['Starttid'], r'%H:%M')
        self.slutdatum = datetime.strptime(data['Slutdatum'], r'%Y-%m-%d')
        self.sluttid = datetime.strptime(data['Sluttid'], r'%H:%M')

    def __str__(self):
        return f'[{self.startdatum.strftime(r"%Y-%m-%d")} {self.starttid.strftime(r"%H:%M")}-{self.sluttid.strftime(r"%H:%M")}] {self.kurs}: {self.undervisningstyp}: '

    def __repr__(self):
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        member_str = ', '.join(f'{member}={getattr(self, member)}' for member in members)
        return f'Event({member_str})'

    def to_dict(self):
        """ Returns a dictionary containing all values needed to be imported
        into a Google Calendar. This method can be rewritten to fit other 
        calendar formats (such as Outlook) or change the output format of
        each field. """ 
        return {
            'Subject': f"{self.kurs}: {self.undervisningstyp}",
            'Start Date': self.startdatum.strftime(r'%m/%d/%Y'),
            'All Day Event': 'FALSE',
            'Start Time': self.starttid.strftime(r'%I:%M %p'),
            'End Time': self.sluttid.strftime(r'%I:%M %p'),
            'Location': self.lokal,
            'Description': self.information
        }