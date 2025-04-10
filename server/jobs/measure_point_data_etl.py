#!/usr/bin/env python
# coding: utf-8

# # Meetdata uploaden database

# Deze notebook zal de actuele minuutwaarden van de ring uploaden in de Postgres database 

# In[309]:


import datetime
import requests 
import xml.etree.ElementTree as ET
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import warnings
from urllib3.exceptions import InsecureRequestWarning


# In[310]:

print(f"Script started at: {datetime.datetime.now()}")
url = "https://miv.opendata.belfla.be/miv/verkeersdata"
warnings.simplefilter('ignore', InsecureRequestWarning)

# In[311]:

resp = requests.get(url, verify=False)
print(resp)


# In[312]:


root = ET.fromstring(resp.text)


# In[313]:


# root[0].text


# In[314]:


# for meetpunt in root:
#     if meetpunt.attrib.get("unieke_id") == "29":
#         for element in meetpunt:
#             print(element)
#             if element.tag == "rekendata" or element.tag == "meetdata":
#                 print(element.attrib)
#                 for x in element:
#                     print(x.tag, x.text)


# Data parsen met behulp van de ElementTree liberary 

# In[315]:


def get_text(parent, child_name):
    """
    Functie die child tekst uit meegegeven parent haalt
    """
    child = parent.find(child_name)
    return child.text if child is not None else None  

data = []
for meetpunt in root:
    if meetpunt.tag != "meetpunt":
        continue
    meetpuntdata = {} 
    meetpuntdata["unieke_id"] = int(meetpunt.attrib.get("unieke_id"))
    meetpuntdata["tijd_waarneming"] = get_text(meetpunt, "tijd_waarneming")
    meetpuntdata["actueel_publicatie"] = bool(int(get_text(meetpunt, "actueel_publicatie")))
    meetpuntdata["beschikbaar"] = bool(int(get_text(meetpunt, "beschikbaar")))
    meetpuntdata["defect"] = bool(int(get_text(meetpunt, "defect")))
    meetpuntdata["geldig"] = bool(int(get_text(meetpunt, "geldig")))
    
    for element in meetpunt:
        if element.tag == "meetdata":
            klasse_id = element.attrib.get("klasse_id")
            if klasse_id:
                meetpuntdata[f"snelheid_rek_{klasse_id}"] = int(get_text(element, "voertuigsnelheid_rekenkundig"))
                meetpuntdata[f"snelheid_har_{klasse_id}"] = int(get_text(element, "voertuigsnelheid_harmonisch"))
        elif element.tag == "rekendata":
            meetpuntdata["bezettingsgraad"] = int(get_text(element, "bezettingsgraad"))
            meetpuntdata["beschikbaarheidsgraad"] = int(get_text(element, "beschikbaarheidsgraad"))
            meetpuntdata["onrustigheid"] = int(get_text(element, "onrustigheid"))
            
    data.append(meetpuntdata)


# In[316]:


df = pd.DataFrame(data)
#df.head(1)


# Verbinden met database om enkel de meetpunten van de ring op te halen

# In[317]:

load_dotenv()


# In[318]:


conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    dbname=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    port=os.getenv('DB_PORT')
)

cur = conn.cursor() 

#tabel aanmaken
cur.execute("""SELECT measurement_id FROM measurement_points""")

meetpunten_sql = cur.fetchall()

conn.commit()

cur.close()
conn.close()


# In[319]:


meetpunten = [x[0] for x in meetpunten_sql] #meetpunten uit tuple halen 


# In[320]:


df_meetdata = df[[df['unieke_id'].iloc[x] in meetpunten for x in range(len(df))]] #enkel meetpunten gebruiken die van toepassing zijn
df_meetdata = df_meetdata[df_meetdata['actueel_publicatie'] == True] #enkel actuele data in db zetten
row_count = len(df_meetdata.index)
#df_meetdata


# Legen tabel maken indien ze nog niet bestaat

# In[321]:


conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    dbname=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    port=os.getenv('DB_PORT')
)

cur = conn.cursor() 

#tabel aanmaken
cur.execute("""CREATE TABLE IF NOT EXISTS measurement_data( 
    unieke_id SMALLINT,
    tijd_waarneming TIMESTAMP,
    actueel_publicatie BOOL,
    beschikbaar TEXT,
    defect BOOL,
    geldig BOOL,
    snelheid_rek_1 SMALLINT,
    snelheid_har_1 SMALLINT,
    snelheid_rek_2 SMALLINT,
    snelheid_har_2 SMALLINT,
    snelheid_rek_3 SMALLINT,
    snelheid_har_3 SMALLINT,
    snelheid_rek_4 SMALLINT,
    snelheid_har_4 SMALLINT,
    snelheid_rek_5 SMALLINT,
    snelheid_har_5 SMALLINT,
    bezettingsgraad SMALLINT,
    beschikbaarheidsgraad SMALLINT,
    onrustigheid SMALLINT
)
""")


# Data van dataframe naar database uploaden

# In[322]:


for i, row in df_meetdata.iterrows():
    
    values = (row.loc['unieke_id'], row.loc['tijd_waarneming'], row.loc['actueel_publicatie'], row.loc['beschikbaar'], row.loc['defect'], row.loc['geldig'], 
              row.loc['snelheid_rek_1'], row.loc['snelheid_har_1'],row.loc['snelheid_rek_2'], row.loc['snelheid_har_2'],row.loc['snelheid_rek_3'], row.loc['snelheid_har_3'], 
              row.loc['snelheid_rek_4'], row.loc['snelheid_har_4'], row.loc['snelheid_rek_5'], row.loc['snelheid_har_5'], row.loc['bezettingsgraad'], row.loc['beschikbaarheidsgraad'], 
              row.loc['onrustigheid'])
    
    cur.execute(""" INSERT INTO measurement_data ( 
                        unieke_id, tijd_waarneming, actueel_publicatie, beschikbaar, defect,
                        geldig, snelheid_rek_1, snelheid_har_1, snelheid_rek_2, snelheid_har_2, snelheid_rek_3,
                        snelheid_har_3, snelheid_rek_4, snelheid_har_4, snelheid_rek_5, snelheid_har_5, bezettingsgraad,
                        beschikbaarheidsgraad, onrustigheid) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", values)


# In[323]:


conn.commit()

cur.close()
conn.close()

print(f"Rowcount: {row_count}")
print(f"Script ended at: {datetime.datetime.now()}")

