# Prototype AI-MDM

## Installatie

We gaan er bij deze installatiegids van uit dat Python en git reeds zijn geïnstalleerd.

Download de source code, bv. via `git pull` of `git clone`
```
git clone https://github.com/hogent-cads/AI_MDM_Prototype.git
```

Maak een virtuele omgeving aan, bv. met `virtuelenv`.
```
cd AI_MDM_Prototype
mkdir envs
python -m venv envs/ai-mdm
```

Dit maakt een nieuwe directory aan `mdm-st` aan. 

Activeer nu de virtuele omgeving:
```
source envs/ai-mdm/bin/activate 
```
Installeer de vereisten in de virtuele omgeving:
```
pip install -r requirements.txt
```

### Backend installatie

Als je de backend wil uitvoeren op een andere computer dan de
frontend dan kan je deze sectie volgen.

Als je de backend wil uitvoeren m.b.v. `gunicorn` dan 
moet deze ook geïnstalleerd worden:
```
pip install gunicorn
```
Hierna kan je de backend opstarten 
```
gunicorn -w 3 run_flask:app
```
Dit commando moet je uitvoeren in de directory die het bestand `run_flask.py` bevat.
Hierna zal de backend beschikbaar zijn op poort 8000 (maar enkel 
vanaf je eigen computer!)

### Frontend starten op je eigen computer

Het starten van de frontend op je eigen computer is gemakkelijk.
Zorg ervoor dat de `ai-mdm` virtuele omgeving actief is.

Voer het volgende commando uit:
```
streamlit run run_streamlit.py
```
Dit start de streamlit app op en opent een browser.

### Reverse proxy instellen voor `gunicorn`






 
