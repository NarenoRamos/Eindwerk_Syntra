# Eindwerk Data Science - Syntra

## Beschrijving

Deze repository bevat mijn  eindwerk voor het eerste jaar van de opleiding Data Science aan Syntra. Het doel van dit project was om het verkeer op de ring van Antwerpen te visualiseren.

De volgende gegevensbronnen werden gebruikt voor dit project:

- [Minuutwaarden van verkeersmetingen in Vlaanderen](https://www.vlaanderen.be/datavindplaats/catalogus/meten-in-vlaanderen-minuutwaarden-verkeersmetingen): Deze gegevens bevatten gedetailleerde informatie over het verkeer, gemeten per minuut.
- [Wegenregister van het Opendata portaal van Antwerpen](https://portaal-stadantwerpen.opendata.arcgis.com/datasets/62c498e88d8749b48b5bc873e00f65ff_297/explore): Het wegenregister biedt gedetailleerde informatie over de wegen en infrastructuur in de regio Antwerpen.

De minuutwaarden worden verzameld door een **Python-script**, dat elke vijf minuten wordt uitgevoerd via een **cron job** en de gegevens vervolgens opslaat in een **PostgreSQL-database**.
 Vervolgens worden de gegevens via een **Flask backend** beschikbaar gesteld via een API. Een **Vite-React client** haalt de gegevens op en toont ze aan de gebruiker. De client communiceert met de backend via een **Nginx reverse proxy**.

## Installatie
Dit project draait in Docker, dus het is noodzakelijk om Docker geïnstalleerd te hebben op je apparaat om het project lokaal te kunnen uitvoeren. Volg onderstaande stappen om dit project lokaal op te zetten:

#### 1. **Clone repository**

 ```bash
 git clone https://github.com/NarenoRamos/Eindwerk_Syntra.git
 ```
 
#### 2. **Conifigureer de .env file**
Vul de poorten 
#### 3. **Maak Docker netwerk aan**

 ```bash
 docker network create mynetwork
 ```
#### 4. **Run docker compose**

 ```bash
 docker compose up -d
 ```
#### 5. Database intitialisatie
De link van de Jupyter server is terug te vinden door de logs te openen van de Jupyter container:
 ```bash
 docker logs jupyter-server
 ```

Daarna mogen de 3 notebooks gerund worden om de initiele tabellen in de PostgresSQL databank te krijgen. 
