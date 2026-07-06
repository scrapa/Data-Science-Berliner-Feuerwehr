```text
Analyse der Einsatzstruktur und Hilfsfristen der Berliner Feuerwehr (2023)
Modul: Einführung Data Science (Prof. Dr. Christin Schmidt)
Institution: HTW Berlin, FB4, Studiengang Angewandte Informatik
Semester: Sommersemester 2026
Gruppe: 6

1. Projektbeschreibung
Dieses Data-Science-Projekt analysiert das Einsatzaufkommen und die raumstrukturelle Abdeckung der Berliner Feuerwehr im Kalenderjahr 2023. Ziel der Arbeit ist es, die Verteilung der Notfälle, die Einhaltung der Hilfsfristen und den Zusammenhang zwischen der städtischen Bevölkerungsdichte und der Einsatzlast datengestützt und reproduzierbar zu untersuchen.

2. Team und Rollenverteilung
Die Umsetzung des Projekts erfolgt in einer fünfköpfigen Arbeitsgruppe. Zur effizienten Bearbeitung wurden folgende Rollen und Verantwortlichkeiten definiert:

Attila Kalafat (599121) – Domain Expert & Projektleitung: Übernimmt die inhaltliche Führung, verantwortet die Theoriebildung und steuert den Projektablauf.

Adam Kefi (593033) – Data Engineer: Ist für die Datenaufbereitung, die Bereinigung der Datensätze sowie die technische Infrastruktur zuständig.

Paul Giorgobiani (597628) – Time-Series Analyst: Analysiert zeitliche Trends und Muster.

Al-Zubair Al-Abbasi (586840) – Geospatial Analyst: Untersucht räumliche Verteilungen und wertet geografische Faktoren aus.

Sipan Cheikhi (600279) – Statistical Modeler: Verantwortet die mathematisch-statistische Modellierung (mittels multipler linearer Regression) und die tiefergehende Ursachenforschung.

3. Verwendete Datenquellen
Das Projekt basiert ausschließlich auf öffentlich zugänglichen, amtlichen Sekundärdaten:

Berliner Feuerwehr Open Data (2023): Enthält 512.885 anonymisierte Einsatzdatensätze (Datum, Einsatzart, Bezirk, Hilfsfrist).

Zensus (Stichtag 15.05.2022): Demografische Daten (Einwohnerzahl, Bevölkerungsdichte) der 12 Berliner Bezirke (Destatis).

Feuerwehrstandorte Berlin: Geodaten zu den exakten Standorten (WGS 84) von 102 Wachen der Berufs- und Freiwilligen Feuerwehr (Geoportal Berlin).

4. Projektstruktur (Repository)
Um die Reproduzierbarkeit der Analysen zu gewährleisten, ist das Projekt wie folgt strukturiert:
```text
/
├── data/
│   ├── raw/                              # Unveränderte Originaldaten
│   │   ├── mission_data_set_open_data_2023.csv
│   │   ├── Zensus_Datenportal.csv
│   │   ├── feuerwehr_a_feuerwehr_standorte_WGS84.csv
│   │   └── bezirke_centroids.csv         # Manuell extrahierte Bezirksmittelpunkte
│   ├── processed/                        # Bereinigte Daten (Ergebnis aus Person 2)
│   │   └── incidents_2023_cleaned_TEAM.csv
├── code/
│   ├── 01_daten_aufbereitung.R           # Pipeline Person 2 (Cleaning & Feature Engineering)
│   ├── 02_deskriptive_analyse.R          # Auswertungen Person 1
│   └── 03_hilfsfristen_analyse.R         # Auswertungen Person 3
├── docs/
│   ├── Seminararbeit_Gruppe6.pdf         # Finale schriftliche Ausarbeitung
│   └── Praesentation_Gruppe6.pdf         # Folien für die Abschlusspräsentation
└── README.md                             # Diese Projektübersicht


5. Setup und Reproduzierbarkeit
Die gesamte Datenverarbeitung und Analyse wurde in R durchgeführt. Zur lokalen Reproduktion des Projekts müssen folgende Voraussetzungen erfüllt sein:
Benötigte R-Pakete:
tidyverse (Datenmanipulation, Joins und Visualisierung mit ggplot2)
sf (Geometrische Transformationen, Distanzberechnungen, EPSG-Projektionen)

Ausführung:
Repository klonen / ZIP-Ordner entpacken.
Das Skript code/01_daten_aufbereitung.R ausführen. Dieses Skript liest die Rohdaten ein, berechnet die fehlenden Flächen/Distanzen und generiert die Datei incidents_2023_cleaned_TEAM.csv.
Anschließend können die Analyse-Skripte 02_deskriptive_analyse.R und 03_hilfsfristen_analyse.R unabhängig voneinander ausgeführt werden, da sie beide auf den sauberen Master-Datensatz zugreifen.

6. Methodische Hinweise und Einschränkungen
Aufgrund strikter Datenschutzvorgaben enthält der Open-Data-Satz der Feuerwehr keine adressgenauen Einsatzorte, sondern aggregiert diese auf Bezirksebene. Alle im Rahmen dieses Projekts berechneten räumlichen Metriken (insbesondere die Distanz zur nächsten Wache) basieren daher auf den Bezirksmittelpunkten und dienen als analytischer Proxy, nicht als exakte Einsatzdistanzen. Details hierzu sind in Kapitel 2.3 der Seminararbeit dokumentiert.
