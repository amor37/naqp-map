# naqp-map
# 🎙️ Non Aprite Quella Podcast - Mappa Interattiva (CON GEOCODING IBRIDO)

Mappa interattiva dei casi del podcast "Non Aprite Quella" con **aggiornamento automatico da Spotify** e **geocoding intelligente**.

## ✨ Novità: Geocoding Ibrido

**Come funziona:**
1. ✅ **Locations note** (locations_map) → Veloci (0 secondi)
2. 🌍 **Locations sconosciute** → Geocoding automatico (1-2 secondi)
3. 📊 **Tempo totale** → 30-45 secondi (veloce!)

**Beneficio:** La mappa scopre AUTOMATICAMENTE nuove locations mentre elabora gli episodi! 🎉

---

## 📋 File Necessari

Scarica questi **4 file**:

1. **`extract_episodes_hybrid.py`** - Script Python con geocoding ibrido ⭐ NUOVO
2. **`requirements.txt`** - Dipendenze Python ⭐ NUOVO
3. **`update-map-hybrid.yml`** - GitHub Actions workflow (va nella cartella `.github/workflows/`)
4. **`index.html`** - Mappa interattiva (se non hai già il progetto)

---

## 🚀 Setup Rapido (10 minuti)

### Step 1: Crea il Repository su GitHub

1. Vai su GitHub → **"New repository"**
2. Chiama il repo: `podcast-map`
3. Rendi pubblico ✅
4. Clicca **"Create repository"**

### Step 2: Carica i File

**Via interfaccia GitHub (facile):**

1. Nel repo, clicca **"Add file"** → **"Upload files"**
2. Trascina questi file:
   - `extract_episodes_hybrid.py`
   - `requirements.txt`
   - `index.html`
3. Crea il workflow:
   - Clicca **"Add file"** → **"Create new file"**
   - Scrivi il path: `.github/workflows/update-map.yml`
   - Incolla il contenuto di `update-map-hybrid.yml`
   - Clicca **"Commit new file"**

**Oppure via command line:**

```bash
git clone https://github.com/TUO_USERNAME/podcast-map.git
cd podcast-map

# Copia i file
cp extract_episodes_hybrid.py .
cp requirements.txt .
cp index.html .

# Crea la cartella del workflow
mkdir -p .github/workflows
cp update-map-hybrid.yml .github/workflows/update-map.yml

git add .
git commit -m "Initial commit: podcast map con geocoding ibrido"
git push
```

### Step 3: Configura i Secrets ⚠️ IMPORTANTE

1. Vai nel repo → **Settings** (tab in alto)
2. Sidebar sinistra → **"Secrets and variables"** → **"Actions"**
3. Clicca **"New repository secret"**

**Aggiungi 2 secrets:**

#### Secret 1
- **Name:** `SPOTIFY_CLIENT_ID`
- **Value:** `ef7c256d88a042d79e84808027ab94d7`
- Clicca **"Add secret"**

#### Secret 2
- **Name:** `SPOTIFY_CLIENT_SECRET`
- **Value:** `4a10712a39804669ad8a098cdf347f0b`
- Clicca **"Add secret"**

Dovresti vederli entrambi con ✅

### Step 4: Testa il Workflow

1. Vai nel repo → **Actions** (tab in alto)
2. Clicca **"Update Podcast Map"** (il workflow appena creato)
3. Clicca il pulsante **"Run workflow"** (a destra)
4. Scegli il branch: `main` e clicca **"Run workflow"**

**Attendi 45-60 secondi** per il completamento.

### Step 5: Verifica il Risultato

1. Torna alla pagina principale del repo
2. Dovresti vedere il file **`episodi_map.json`** creato automaticamente
3. Se lo vedi → ✅ **Perfetto!**

### Step 6: Visualizza i Log (Importante!)

Nel workflow appena eseguito, **espandi i log** per vedere:
- ✅ Quanti episodi con location sono stati trovati
- 🌍 Quali locations sono state scoperte automaticamente (geocoding)
- ❓ Quali locations NON sono state trovate (da aggiungere?)

Questo è molto utile per migliorare locations_map!

### Step 7: Abilita GitHub Pages (Opzionale)

Se vuoi che la mappa sia online:

1. **Settings** → **Pages**
2. **Source:** "Deploy from a branch"
3. **Branch:** `main` / **Folder:** `/ (root)`
4. Clicca **"Save"**

Dopo 1-2 minuti la mappa sarà disponibile su:
```
https://TUO_USERNAME.github.io/podcast-map/
```

---

## 🔄 Come Funziona

### Automatico (ogni domenica)

Ogni domenica alle 10:00 UTC:
1. ⚙️ GitHub Actions esegue `extract_episodes_hybrid.py`
2. 🔍 Lo script scarica gli episodi da Spotify
3. 📍 Cerca locations in locations_map (veloce)
4. 🌍 Se non trovata, chiama Geopy per geocoding (1-2 sec)
5. 📊 Genera `episodi_map.json`
6. 💾 Se ci sono cambiamenti, committa e pusha il file

### Manuale (quando vuoi)

Vai in **Actions** → **"Update Podcast Map"** → **"Run workflow"**

---

## 📊 Cosa Genera Lo Script

### File creato: `episodi_map.json`

```json
[
  {
    "numero": 1,
    "titolo": "Il Caso di Parabiago",
    "data_rilascio": "2024-01-15",
    "stagione": 1,
    "descrizione": "...",
    "lat": 45.5417,
    "lng": 8.9336,
    "continent": "italia",
    "url_episodio": "https://...",
    "durata_ms": 1234567,
    "location_type": "known"  // 'known' o 'geocoded'
  },
  ...
]
```

### Output nel Log (Importante!)

```
📊 STATISTICHE:
✅ Episodi con location: 60
⚠️  Episodi senza location: 25
   - Da locations_map: 50 ✅
   - Da geocoding: 10 🌍

🌍 LOCATIONS SCOPERTE AUTOMATICAMENTE (10):
   - Berlin: (52.52°, 13.40°)
   - Tokyo: (35.68°, 139.65°)
   - Sydney: (-33.87°, 151.21°)
   ...

❓ LOCATIONS NON TROVATE (5):
   - Neverland (3x)
   - Atlantide (2x)
   ...

💡 Aggiungi queste locations a locations_map per velocizzare!
```

---

## 🎯 Prossimi Passaggi

### Subito (Setup iniziale)

1. ✅ Esegui il workflow manualmente
2. ✅ Leggi i log per vedere le locations scoperte
3. ✅ Verifica episodi_map.json

### Successivamente (Miglioramento)

Se nel log vedi **❓ LOCATIONS NON TROVATE**, puoi:

#### Opzione A: Aggiungere manualmente a locations_map

Nel file `extract_episodes_hybrid.py`, sezione `load_or_create_locations_map()`:

```python
def load_or_create_locations_map():
    locations_map = {
        'Parabiago': {'lat': 45.5417, 'lng': 8.9336, 'continent': 'italia'},
        # Aggiungi qui le nuove locations
        'Berlin': {'lat': 52.52, 'lng': 13.40, 'continent': 'europa'},  # ← Nuovo
        'Tokyo': {'lat': 35.68, 'lng': 139.65, 'continent': 'mondo'},   # ← Nuovo
    }
```

#### Opzione B: Lasciare il geocoding automatico

Se nel log vedi **🌍 LOCATIONS SCOPERTE AUTOMATICAMENTE**, significa che il geocoding ha trovato le coordinate automaticamente! Non devi fare nulla. 🎉

---

## ❌ Troubleshooting

### "episodi_map.json non viene creato"

1. Vai in **Actions** → **"Update Podcast Map"**
2. Clicca sul job fallito
3. **Espandi tutti i step** e cerca il messaggio di errore

**Cause comuni:**

| Errore | Soluzione |
|--------|-----------|
| "Credenziali non trovate" | Verifica i secrets in Settings → Secrets |
| "Errore di rete" | Problema con Spotify API, riprova più tardi |
| "FileNotFoundError: extract_episodes_hybrid.py" | Assicurati che `extract_episodes_hybrid.py` sia nella cartella root |
| "ModuleNotFoundError: geopy" | Il file `requirements.txt` deve essere caricato |
| "HTTP 401 Unauthorized" | I secrets Spotify sono scaduti o errati |

### "Workflow non trova il file Python"

✅ Verifica che:
- [ ] `extract_episodes_hybrid.py` è nella **cartella root** (non in sottocartelle)
- [ ] `requirements.txt` è nella **cartella root**
- [ ] `.github/workflows/update-map.yml` è nella **cartella .github/workflows**

### "Geopy time out" o "Nominatim blocked"

Questo significa che Nominatim (OpenStreetMap) è temporaneamente saturo.

**Soluzione:**
1. Attendi 5-10 minuti
2. Esegui il workflow di nuovo

---

## 🔍 Monitor del Geocoding

Nel log vedrai:

```
🔍 Estrazione locations (può richiedere 30-45 secondi)...
   📍 Locations note caricate: 35
   🔍 Ricerca del podcast 'Non Aprite Quella'...
   ✅ Podcast trovato: Non Aprite Quella
   📥 Scaricamento degli episodi...
   📊 Scaricati 10 episodi...
   📊 Scaricati 50 episodi...
   ✅ Totale episodi scaricati: 147
   
   🔍 Estrazione locations...
   🌍 Geocoding per 'Berlin'... ✅ Trovato (52.52°, 13.40°)
   🌍 Geocoding per 'Tokyo'... ✅ Trovato (35.68°, 139.65°)
   🌍 Geocoding per 'Atlantide'... ❌ Non trovato
```

---

## 📚 Struttura del Progetto

```
podcast-map/
├── 📄 extract_episodes_hybrid.py     ← Script Python con geocoding
├── 📄 requirements.txt                ← Dipendenze (requests, geopy)
├── 📄 index.html                      ← Mappa interattiva
├── 📄 episodi_map.json                ← Dati generati (auto)
├── 📄 README.md                       ← Questo file
└── 📁 .github/workflows/
    └── 📄 update-map.yml              ← GitHub Actions workflow
```

---

## ✨ Funzionalità

- ✅ **Carica automaticamente** episodi da Spotify
- ✅ **Locations note** da locations_map (veloce)
- ✅ **Geocoding automatico** per locations sconosciute (smart)
- ✅ **Rate limiting** per non sovraccaricare Nominatim
- ✅ **Filtra** per continente e stagione
- ✅ **Ricerca** in tempo reale
- ✅ **Dark mode** automatico
- ✅ **Responsive** (mobile + desktop)
- ✅ **Aggiornamento automatico** ogni domenica
- ✅ **Zero interventi manuali** dopo setup

---

## 🔒 Sicurezza

Le credenziali Spotify sono **protette**:
- Salvate come GitHub Secrets (non visibili pubblicamente)
- Non appaiono nei log
- Non vengono mai committate nel repo

---

## 📝 Note

- Il workflow gira su **GitHub Actions** (gratuito)
- GitHub **Pages** per l'hosting (gratuito)
- **Nessun costo ricorrente**
- Dati aggiornati **automaticamente ogni domenica**
- Geocoding con **Nominatim/OpenStreetMap** (gratuito e open-source)

---

## 🆘 Aiuto

Se hai problemi:

1. **Leggi i logs** in **Actions** (espandi tutti i step)
2. **Controlla i secrets** in **Settings** → **Secrets and variables**
3. **Verifica i file** siano nel posto giusto
4. **Leggi il messaggio di errore** attentamente
5. Attendi se Nominatim è saturo (retry dopo 5 minuti)

---

## 🚀 Versione Successiva

Idea per il futuro:
- [ ] Cache di locations geocoded (per velocizzare)
- [ ] UI per approvare/rifiutare locations auto-scoperte
- [ ] Visualizzazione statistics sulla mappa
- [ ] Export dati in diversi formati

---

**Creato con ❤️ per "Non Aprite Quella" Podcast**
