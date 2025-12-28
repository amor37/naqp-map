# Versione completa che scarica davvero da Spotify
import requests
import json

CLIENT_ID = 'ef7c256d88a042d79e84808027ab94d7'
CLIENT_SECRET = '4a10712a39804669ad8a098cdf347f0b'

# 1. Autenticazione
auth = (CLIENT_ID, CLIENT_SECRET)
response = requests.post('https://accounts.spotify.com/api/token',
                         data={'grant_type': 'client_credentials'},
                         auth=auth)
token = response.json()['access_token']

# 2. Ricerca podcast
search = requests.get('https://api.spotify.com/v1/search',
                     headers={'Authorization': f'Bearer {token}'},
                     params={'q': 'Non Aprite Quella', 'type': 'show', 'limit': 1})
show_id = search.json()['shows']['items'][0]['id']

# 3. Scarica episodi
episodes = []
offset = 0
while True:
    resp = requests.get(f'https://api.spotify.com/v1/shows/{show_id}/episodes',
                       headers={'Authorization': f'Bearer {token}'},
                       params={'limit': 50, 'offset': offset})
    items = resp.json()['items']
    episodes.extend(items)
    if not resp.json().get('next'):
        break
    offset += 50

# 4. Salva
with open('episodi.json', 'w') as f:
    json.dump(episodes, f)
