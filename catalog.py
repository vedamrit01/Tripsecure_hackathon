"""Curated demo catalogue. Prices, durations and coordinates are planning assumptions."""
SOURCES = {
    'rishikesh': {'url': 'https://www.uttarakhandtourism.gov.in/destination/rishikesh', 'publisher': 'Uttarakhand Tourism', 'scope': 'Destination background; does not verify our estimated prices or schedules.'},
    'jaipur': {'url': 'https://www.tourism.rajasthan.gov.in/jaipur.html', 'publisher': 'Rajasthan Tourism', 'scope': 'Destination and attraction background; does not verify our estimated prices or schedules.'},
}
DESTINATIONS = {
    'Rishikesh': {'lat': 30.0869, 'lon': 78.2676, 'source': 'rishikesh', 'tags': ['nature', 'food', 'wellness'], 'travel_hours': 7, 'transport_pp': 1800, 'comfort_room': 3000, 'value_room': 1500},
    'Jaipur': {'lat': 26.9124, 'lon': 75.7873, 'source': 'jaipur', 'tags': ['culture', 'food', 'shopping'], 'travel_hours': 6, 'transport_pp': 1400, 'comfort_room': 2800, 'value_room': 1400},
}
# id, title, tags, outdoor, estimated activity cost/person, duration hours, lat, lon
_RAW = {
 'Rishikesh': [
 ('r1','Ganges riverside walk',['nature'],True,0,2,30.124,78.322),
 ('r2','Triveni Ghat visit',['culture','nature'],True,0,2,30.103,78.304),
 ('r3','Beatles Ashram visit',['culture','nature'],True,300,2,30.109,78.318),
 ('r4','Tapovan café and local food',['food'],False,250,2,30.129,78.325),
 ('r5','Indoor yoga session',['wellness'],False,400,2,30.126,78.321),
 ('r6','Local vegetarian cooking workshop',['food','culture'],False,800,2,30.122,78.319),
 ('r7','Local craft browsing',['shopping','culture'],False,0,2,30.119,78.315),
 ('r8','Quiet reading at a café',['wellness','food'],False,150,2,30.125,78.324),
 ('r9','Guided meditation session',['wellness'],False,300,2,30.124,78.320),
 ('r10','Riverside photography walk',['nature'],True,0,2,30.121,78.321),
 ('r11','Tea tasting at a local café',['food'],False,200,2,30.127,78.323),
 ('r12','Free afternoon at your accommodation',['wellness'],False,0,2,30.123,78.320),
 ],
 'Jaipur': [
 ('j1','Amber Palace visit',['culture'],True,500,3,26.986,75.851),
 ('j2','Hawa Mahal exterior photography',['culture'],True,0,2,26.924,75.827),
 ('j3','City Palace visit',['culture'],True,700,2,26.925,75.823),
 ('j4','Albert Hall Museum visit',['culture'],False,300,2,26.912,75.819),
 ('j5','Rajasthani cooking workshop',['food','culture'],False,800,2,26.920,75.810),
 ('j6','Local thali experience',['food'],False,300,2,26.916,75.813),
 ('j7','Jal Mahal lakeside walk',['nature'],True,0,2,26.953,75.846),
 ('j8','Indoor block-printing workshop',['culture','shopping'],False,600,2,26.917,75.815),
 ('j9','Local tea and sweets tasting',['food'],False,200,2,26.920,75.821),
 ('j10','Johari Bazaar walk',['shopping','culture'],True,0,2,26.920,75.826),
 ('j11','Café and reading break',['wellness','food'],False,150,2,26.916,75.817),
 ('j12','Free afternoon at your accommodation',['wellness'],False,0,2,26.914,75.814),
 ]}
ACTIVITIES = {city: [dict(zip(['id','title','tags','outdoor','cost_pp','hours','lat','lon'], row), source=DESTINATIONS[city]['source']) for row in rows] for city, rows in _RAW.items()}
