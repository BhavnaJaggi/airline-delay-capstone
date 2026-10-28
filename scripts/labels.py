"""Full-name labels for chart axes and tables (no airline or airport codes in anything a reader sees).

The BTS tables identify carriers and airports by short codes. These dictionaries turn the codes that
occur in this project into full names; a code that is not listed is returned unchanged.
"""

MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
DOW_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]   # BTS: 1 = Monday

CARRIER_NAMES = {
    "9E": "Endeavor Air", "AA": "American Airlines", "AS": "Alaska Airlines", "B6": "JetBlue Airways",
    "DL": "Delta Air Lines", "F9": "Frontier Airlines", "G4": "Allegiant Air", "HA": "Hawaiian Airlines",
    "MQ": "Envoy Air", "NK": "Spirit Airlines", "OH": "PSA Airlines", "OO": "SkyWest Airlines",
    "UA": "United Airlines", "WN": "Southwest Airlines", "YX": "Republic Airways",
    "QX": "Horizon Air", "YV": "Mesa Airlines", "ZW": "Air Wisconsin", "G7": "GoJet Airlines", "EV": "ExpressJet Airlines",
}

AIRPORT_NAMES = {
    "ATL": "Atlanta Hartsfield-Jackson", "BOS": "Boston Logan", "CLT": "Charlotte Douglas", "DCA": "Washington Reagan National",
    "DEN": "Denver International", "DFW": "Dallas/Fort Worth", "DTW": "Detroit Metropolitan", "LAS": "Las Vegas Harry Reid",
    "LAX": "Los Angeles International", "LGA": "New York LaGuardia", "MCO": "Orlando International", "ORD": "Chicago O'Hare",
    "PHX": "Phoenix Sky Harbor", "SEA": "Seattle-Tacoma", "SFO": "San Francisco International", "JFK": "New York John F. Kennedy",
    "EWR": "Newark Liberty", "MIA": "Miami International", "IAH": "Houston George Bush", "MSP": "Minneapolis-Saint Paul",
    "FLL": "Fort Lauderdale-Hollywood", "PHL": "Philadelphia International", "SLC": "Salt Lake City", "BWI": "Baltimore/Washington",
    "SAN": "San Diego International", "TPA": "Tampa International", "IAD": "Washington Dulles", "MDW": "Chicago Midway",
    "HNL": "Honolulu Daniel K. Inouye", "PDX": "Portland International", "AUS": "Austin-Bergstrom", "BNA": "Nashville International",
    "DAL": "Dallas Love Field", "STL": "St. Louis Lambert", "OAK": "Oakland International", "SJC": "San Jose Mineta",
    "SMF": "Sacramento International", "RDU": "Raleigh-Durham", "MCI": "Kansas City International", "HOU": "Houston Hobby",
}


def carrier_name(code):
    return CARRIER_NAMES.get(str(code), str(code))


def airport_name(code):
    return AIRPORT_NAMES.get(str(code), str(code))
