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

## Zingg & Apache Spark Installatie:

Zingg: Versie: zingg-0.3.4-SNAPSHOT-spark-3.1.2
https://github.com/zinggAI/zingg/releases

Spark: Versie : spark-3.1.2-bin-hadoop3.2
https://archive.apache.org/dist/spark/spark-3.1.2/

Zingg Installatie instructies:
https://docs.zingg.ai/zingg/stepbystep/installation/installing-from-release/single-machine-setup

Verifieer de installatie:
https://docs.zingg.ai/zingg/stepbystep/installation/installing-from-release/verification

Algemene structuur Zingg:
model
-MODELID
--model
--trainingData
---marked
----\***\*.parquet files (Na labelingsfase)
---unmarked
----\*\*\***.parquet files (Na findTrainingdatafase)

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
vanaf de server die gunicorn draait!)

### Frontend starten op je eigen computer

Het starten van de frontend op je eigen computer is gemakkelijk.
Zorg ervoor dat de `ai-mdm` virtuele omgeving actief is.

Voer het volgende commando uit:

```
streamlit run run_streamlit.py
```

Dit start de streamlit app op en opent een browser.

### Reverse proxy instellen voor `gunicorn`

Zorg dat `nginx` geïnstalleerd is op de server, bv. op Alma Linux

```
sudo dnf install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

Voeg het volgende blok toe onder `http` in de `nginx` configuratie file
bv. op `/etc/nginx/nginx.conf`.

```
 server {
        listen 80;
        server_name 127.0.0.1; # vervang dit door de server naam

        location / {
           proxy_pass http://127.0.0.1:8000; #  gebruik dezelfde poort als voorheen
        }
    }

```

### Frontend op de server

Zorg dat de virtuele omgeving is geactiveerd. Start de streamlit app als volgt op:

```
streamlit run run_streamlit.py --server.port 8501 --server.baseUrlPath /aimdmtool/ --server.enableCORS true --server.enableXsrfProtection true --server.headless=true
```

In `/etc/nginx/nginx.conf` voeg de volgende configuratie toe die `/aimdmtool`
zal forwarden naar de streamlit applicatie:

```
location /aimdmtool {
          proxy_pass http://127.0.0.1:8501;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header Host $http_host;
          proxy_redirect off;
          proxy_http_version 1.1;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection "upgrade";
        }
```

Voeg dit toe net voor de `location` die de forwarding doet naar `gunicorn`.
