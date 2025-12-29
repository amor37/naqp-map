#!/usr/bin/env python3
"""
Script per estrarre episodi da Spotify e generare JSON per la mappa
Con geocoding ibrido: locations_map veloce + Geopy per locations sconosciute
"""
import requests
import json
import re
from datetime import datetime
import base64
import os
import sys
import time

try:
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    print("⚠️  Geopy non installato. Installa con: pip install geopy")

# Credenziali Spotify
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Inizializza geocoder (se disponibile)
if GEOPY_AVAILABLE:
    geolocator = Nominatim(user_agent="podcast_map")

def get_spotify_token():
    """Ottiene il token di autenticazione da Spotify"""
    try:
        # Verifica credenziali
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            print("❌ ERRORE: Credenziali Spotify non trovate!")
            print(f"   SPOTIFY_CLIENT_ID: {'✅ presente' if SPOTIFY_CLIENT_ID else '❌ mancante'}")
            print(f"   SPOTIFY_CLIENT_SECRET: {'✅ presente' if SPOTIFY_CLIENT_SECRET else '❌ mancante'}")
            return None

        print("🔐 Autenticazione con Spotify...")
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_data = {'grant_type': 'client_credentials'}
        auth_headers = {
            'Authorization': 'Basic ' + base64.b64encode(
                f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'.encode()
            ).decode()
        }

        response = requests.post(auth_url, data=auth_data, headers=auth_headers, timeout=10)
        response.raise_for_status()

        token = response.json()['access_token']
        print("✅ Token ottenuto con successo!")
        return token

    except requests.exceptions.RequestException as e:
        print(f"❌ Errore di rete durante autenticazione: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"❌ Errore nel parsing della risposta Spotify: {e}")
        return None
    except Exception as e:
        print(f"❌ Errore sconosciuto durante autenticazione: {e}")
        return None

def search_podcast(token):
    """Cerca il podcast 'Non Aprite Quella'"""
    try:
        print("🔍 Ricerca del podcast 'Non Aprite Quella'...")
        search_url = 'https://api.spotify.com/v1/search'
        headers = {'Authorization': f'Bearer {token}'}
        params = {'q': 'Non Aprite Quella', 'type': 'show', 'limit': 1}

        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        shows = data.get('shows', {}).get('items', [])

        if shows:
            show_id = shows[0]['id']
            show_name = shows[0]['name']
            print(f"✅ Podcast trovato: {show_name}")
            return show_id
        else:
            print("❌ Podcast non trovato su Spotify")
            return None

    except Exception as e:
        print(f"❌ Errore ricerca podcast: {e}")
        return None

def get_all_episodes(token, show_id):
    """Scarica tutti gli episodi del podcast"""
    try:
        print("📥 Scaricamento degli episodi...")
        episodes_url = f'https://api.spotify.com/v1/shows/{show_id}/episodes'
        headers = {'Authorization': f'Bearer {token}'}

        all_episodes = []
        offset = 0
        limit = 50

        while True:
            params = {'limit': limit, 'offset': offset}
            response = requests.get(episodes_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            items = data.get('items', [])
            all_episodes.extend(items)

            print(f"   📊 Scaricati {len(all_episodes)} episodi...")

            if not data.get('next') or len(items) == 0:
                break
            offset += limit

        print(f"✅ Totale episodi scaricati: {len(all_episodes)}")
        return all_episodes

    except Exception as e:
        print(f"❌ Errore scaricamento episodi: {e}")
        return []

def extract_season(name):
    """Estrae il numero di stagione dal titolo"""
    if not name:
        return 0
    match = re.search(r'S(\d+)', name, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def clean_html(text):
    """Rimuove tag HTML dalla descrizione"""
    if not text:
        return ''
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_city_name(description):
    """Estrae il nome della città dalla descrizione"""
    if not description:
        return None
    
    # Strategie di estrazione (in ordine di priorità):
    
    # 1. Cerca pattern "City, Country"
    match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s+([A-Z][a-z]+)', description)
    if match:
        return match.group(1)
    
    # 2. Primo nome proprio (CamelCase)
    match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', description)
    if match:
        city = match.group(1)
        # Esclude parole comuni
        if city not in ['Il', 'The', 'Una', 'Un', 'L', 'Estate', 'Inverno']:
            return city
    
    # 3. Se niente funziona
    return None

def extract_locations_hybrid(description, locations_map):
    """
    Estrae locations con approccio ibrido:
    1. Prova locations_map (veloce)
    2. Se non trovata, usa geocoding Geopy (smart)
    """
    if not description:
        return None, None

    description_lower = description.lower()
    
    # STEP 1: Prova locations note (veloce)
    for location, coords in locations_map.items():
        if location.lower() in description_lower:
            return coords, 'known'

    # STEP 2: Se geopy non disponibile, ritorna None
    if not GEOPY_AVAILABLE:
        return None, None
    
    # STEP 3: Estrai nome città dalla descrizione
    city_name = extract_city_name(description)
    if not city_name:
        return None, None
    
    # STEP 4: Chiama geocoder con rate limiting
    try:
        print(f"   🌍 Geocoding per '{city_name}'...", end='', flush=True)
        time.sleep(1.1)  # Rate limiting: max 1 req al secondo
        
        location = geolocator.geocode(city_name, timeout=5)
        if location:
            coords = {
                'lat': location.latitude,
                'lng': location.longitude,
                'continent': 'auto-discovered'
            }
            print(f" ✅ Trovato ({location.latitude:.2f}°, {location.longitude:.2f}°)")
            return coords, 'geocoded'
        else:
            print(f" ❌ Non trovato")
            return None, None
            
    except Exception as e:
        print(f" ❌ Errore: {e}")
        return None, None

def generate_episode_data(episodes, locations_map):
    """Genera dati per la mappa"""
    data = []
    skipped = 0
    unknown_locations = {}  # {city: count}
    geocoded_locations = {}  # {city: coords}

    for idx, ep in enumerate(episodes, 1):
        season = extract_season(ep.get('name', ''))
        description = clean_html(ep.get('description', ''))
        location, location_type = extract_locations_hybrid(description, locations_map)

        if location:
            data.append({
                'numero': idx,
                'titolo': ep.get('name', 'N/A'),
                'data_rilascio': ep.get('release_date', 'N/A'),
                'stagione': season,
                'descrizione': description[:300],
                'lat': location['lat'],
                'lng': location['lng'],
                'continent': location.get('continent', 'unknown'),
                'url_episodio': ep.get('external_urls', {}).get('spotify', ''),
                'durata_ms': ep.get('duration_ms', 0),
                'location_type': location_type  # 'known' o 'geocoded'
            })
            
            # Track geocoded locations
            if location_type == 'geocoded':
                city = extract_city_name(description)
                if city:
                    geocoded_locations[city] = location
        else:
            skipped += 1
            # Track unknown locations
            city = extract_city_name(description)
            if city:
                unknown_locations[city] = unknown_locations.get(city, 0) + 1

    # Statistics
    print(f"\n📊 STATISTICHE:")
    print(f"✅ Episodi con location: {len(data)}")
    print(f"⚠️  Episodi senza location: {skipped}")
    
    known_count = sum(1 for ep in data if ep.get('location_type') == 'known')
    geocoded_count = sum(1 for ep in data if ep.get('location_type') == 'geocoded')
    
    if known_count > 0:
        print(f"   - Da locations_map: {known_count} ✅")
    if geocoded_count > 0:
        print(f"   - Da geocoding: {geocoded_count} 🌍")
    
    if geocoded_locations:
        print(f"\n🌍 LOCATIONS SCOPERTE AUTOMATICAMENTE ({len(geocoded_locations)}):")
        for city in sorted(geocoded_locations.keys())[:10]:  # Mostra prime 10
            coords = geocoded_locations[city]
            print(f"   - {city}: ({coords['lat']:.2f}°, {coords['lng']:.2f}°)")
        if len(geocoded_locations) > 10:
            print(f"   ... e {len(geocoded_locations) - 10} altre")
    
    if unknown_locations:
        print(f"\n❓ LOCATIONS NON TROVATE ({len(unknown_locations)}):")
        for city in sorted(unknown_locations.keys(), key=lambda x: unknown_locations[x], reverse=True)[:10]:
            count = unknown_locations[city]
            print(f"   - {city} ({count}x)")
        if len(unknown_locations) > 10:
            print(f"   ... e {len(unknown_locations) - 10} altre")
        print(f"\n💡 Aggiungi queste locations a locations_map per velocizzare!")
    
    return data

def load_or_create_locations_map():
    """Carica locations_map o crea una nuova"""
    locations_map = {
        'Parabiago': {'lat': 45.5417, 'lng': 8.9336, 'continent': 'italia'},
        'Parigi': {'lat': 48.8566, 'lng': 2.3522, 'continent': 'europa'},
        'Gévaudan': {'lat': 44.7, 'lng': 3.5, 'continent': 'europa'},
        'Greeley': {'lat': 40.3968, 'lng': -104.6068, 'continent': 'mondo'},
        'Colorado': {'lat': 39.0997, 'lng': -105.3111, 'continent': 'mondo'},
        'Palm Beach': {'lat': 26.7153, 'lng': -80.0534, 'continent': 'mondo'},
        'Florida': {'lat': 27.6648, 'lng': -81.5158, 'continent': 'mondo'},
        'Orem': {'lat': 40.2969, 'lng': -111.6554, 'continent': 'mondo'},
        'Utah': {'lat': 39.0997, 'lng': -111.0937, 'continent': 'mondo'},
        'Ossett': {'lat': 53.6482, 'lng': -1.6292, 'continent': 'europa'},
        'Yorkshire': {'lat': 53.6482, 'lng': -1.6292, 'continent': 'europa'},
        'Londra': {'lat': 51.5074, 'lng': -0.1278, 'continent': 'europa'},
        'Sydney': {'lat': -33.8688, 'lng': 151.2093, 'continent': 'mondo'},
        'Australia': {'lat': -25.2744, 'lng': 133.7751, 'continent': 'mondo'},
        'Pasadena': {'lat': 34.1478, 'lng': -118.1445, 'continent': 'mondo'},
        'California': {'lat': 36.1162, 'lng': -120.0037, 'continent': 'mondo'},
        'Messico': {'lat': 25.6866, 'lng': -100.3161, 'continent': 'mondo'},
        'New York': {'lat': 40.7128, 'lng': -74.0060, 'continent': 'mondo'},
        'Tokyo': {'lat': 35.6762, 'lng': 139.6503, 'continent': 'mondo'},
        'Giappone': {'lat': 36.2048, 'lng': 138.2529, 'continent': 'mondo'},
        'Brasile': {'lat': -15.8267, 'lng': -48.0516, 'continent': 'mondo'},
        'Norvegia': {'lat': 60.4720, 'lng': 8.4689, 'continent': 'europa'},
        'Oslo': {'lat': 59.9139, 'lng': 10.7522, 'continent': 'europa'},
        'Sierra Nevada': {'lat': 39.0, 'lng': -120.5, 'continent': 'mondo'},
        'Perù': {'lat': -12.0463, 'lng': -77.0372, 'continent': 'mondo'},
        'Amazzonia': {'lat': -3.4653, 'lng': -62.2159, 'continent': 'mondo'},
        'New Orleans': {'lat': 29.9511, 'lng': -90.2623, 'continent': 'mondo'},
        'Louisiana': {'lat': 31.1695, 'lng': -91.8749, 'continent': 'mondo'},
        'Grecia': {'lat': 39.0742, 'lng': 21.8243, 'continent': 'europa'},
        'Spagna': {'lat': 42.8160, 'lng': -1.6442, 'continent': 'europa'},
        'Monrovia': {'lat': 6.3156, 'lng': -10.8073, 'continent': 'mondo'},
        'Liberia': {'lat': 6.3156, 'lng': -10.8073, 'continent': 'mondo'},
        'Bruxelles': {'lat': 50.8503, 'lng': 4.3517, 'continent': 'europa'},
        'Belgio': {'lat': 50.5039, 'lng': 4.4699, 'continent': 'europa'},
        'Palermo': {'lat': 38.1157, 'lng': 13.3615, 'continent': 'italia'},
        'Sicilia': {'lat': 37.9769, 'lng': 12.5867, 'continent': 'italia'},
    }
    return locations_map

def main():
    print("\n" + "="*60)
    print("🎙️ Estrazione Episodi - Non Aprite Quella Podcast")
    print("="*60 + "\n")

    # Verifica Geopy
    if not GEOPY_AVAILABLE:
        print("⚠️  AVVISO: Geopy non disponibile!")
        print("   Usa solo locations_map (niente geocoding automatico)")
        print("   Per abilitare: pip install geopy\n")

    # Carica locations_map
    locations_map = load_or_create_locations_map()
    print(f"📍 Locations note caricate: {len(locations_map)}\n")

    # Autenticazione
    token = get_spotify_token()
    if not token:
        print("\n❌ Impossibile autenticarsi con Spotify")
        return False

    # Ricerca podcast
    show_id = search_podcast(token)
    if not show_id:
        print("\n❌ Impossibile trovare il podcast")
        return False

    # Scaricamento episodi
    episodes = get_all_episodes(token, show_id)

    if not episodes:
        print("\n❌ Nessun episodio trovato")
        return False

    # Genera dati
    print("\n🔍 Estrazione locations (può richiedere 30-45 secondi)...\n")
    data = generate_episode_data(episodes, locations_map)

    if not data:
        print("\n⚠️  Nessun episodio con location trovato")
        data = []

    # Salva il JSON
    output_file = 'episodi_map.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Dati salvati in: {output_file}")
        print(f"📅 Data aggiornamento: {datetime.now().isoformat()}")
        print(f"📊 Dimensione file: {os.path.getsize(output_file)} bytes")
        print(f"🗺️  Episodi sulla mappa: {len(data)}\n")

        return True

    except Exception as e:
        print(f"\n❌ Errore durante il salvataggio: {e}")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Errore fatale: {e}")
        sys.exit(1)
