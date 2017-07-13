import requests
import json
from pymongo import MongoClient
import os
import datetime

login = os.environ.get('LOGIN')
password = os.environ.get('PASSWORD')
MONGODB_URI = os.environ.get('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client.get_default_database()

session = requests.Session()

session.get('https://fantasy.premierleague.com/')
csrftoken = session.cookies['csrftoken']
login_data = {
    'csrfmiddlewaretoken': csrftoken,
    'login': login,
    'password': password,
    'app': 'plfpl-web',
    'redirect_uri': 'https://fantasy.premierleague.com/a/login'
}
session.post('https://users.premierleague.com/accounts/login/',
             data=login_data)


# bootstrap-static
bootstrap_static = json.loads(session.get('https://fantasy.premierleague.com/drf/bootstrap-static').text)
bootstrap_static["_id"] = datetime.datetime.utcnow()
db.fpl_bootstrap_static.insert(bootstrap_static)
print("Saved bootstrap-static")

# element-summary
for element in bootstrap_static['elements']:
    element_summary = json.loads(session.get('https://fantasy.premierleague.com/drf/element-summary/'
                                             + str(element['id'])).text)
    element_summary['_id'] = element['id']
    db.fpl_element_summary.replace_one({'_id': element_summary['_id']}, element_summary, upsert=True)
    print('Saved element-summary: ' + str(element_summary['_id']))

# fixtures
fixtures_full = json.loads(session.get('https://fantasy.premierleague.com/drf/fixtures').text)
for fixture in fixtures_full:
    fixture['_id'] = fixture.pop('id')
    db.fpl_fixtures.replace_one({'_id': fixture['_id']}, fixture, upsert=True)
    print('Saved fixture: ' + str(fixture['_id']))

# bootstrap-dynamic
#bootstrap_dynamic = json.loads(session.get('https://fantasy.premierleague.com/drf/bootstrap-dynamic').text)
#print(json.dumps(bootstrap_dynamic))
#bootstrap_dynamic["_id"] = datetime.datetime.utcnow()
#db.fpl_bootstrap_dynamic.insert(bootstrap_dynamic)
