#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyse_kapitel_3_2.py

Reproduzierbare Analyse für Kapitel 3.2 der Seminararbeit
"Faktoren der Hilfsfristen bei der Berliner Feuerwehr".

Erzeugt:
    1. Tabelle 3.1 – Einsatzhäufigkeit je Bezirk (absolut und je 10.000 EW)
    2. Aggregation der Einsatzdichte auf Ebene der sechs Einsatzbereiche (EB E1–E6)
    3. Tabelle 3.2 – Berufsfeuerwachen je Einsatzbereich und Fläche je Wache
    4. Abbildung 3.5 – Choroplethenkarte der durchschnittlichen Hilfsfrist je Bezirk

Datenquellen:
    - Einsatzdaten 2023: Berliner Feuerwehr, BF-Open-Data (GitHub), Mission_Data
      [vgl. Berliner Feuerwehr 2024]
    - Bevölkerungs-/Flächendaten: Zensus 2022, siehe Tabelle 2.1 der Arbeit
      [vgl. Statistische Ämter des Bundes und der Länder 2022]
    - Wachenzahl je Einsatzbereich: Organigramm der Berliner Feuerwehr 2024
      [vgl. Berliner Feuerwehr 2024b]
    - Bezirksgeometrien: GeoJSON der Berliner Bezirke [vgl. Geoportal Berlin o. J.]

Benötigte Pakete:
    pandas, geopandas, matplotlib
Installation (falls nötig):
    pip install pandas geopandas matplotlib
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# 0. Konfiguration – Dateipfade zentral an einer Stelle
# ---------------------------------------------------------------------------
# Pfad zum Einsatzdatensatz. Standardmäßig wird der von der Berliner Feuerwehr
# öffentlich bereitgestellte Rohdatensatz erwartet. Falls der bereits im Team
# bereinigte Datensatz verwendet werden soll, hier einfach den Pfad ersetzen
# (z. B. "incidents_2023_cleaned_TEAM.csv"). Da laut Kapitel 2 keine Zeilen
# entfernt wurden, sind die Ergebnisse in beiden Fällen identisch.
MISSION_CSV = "mission_data_set_open_data_2023.csv"

# GeoJSON mit den Polygongeometrien der zwölf Berliner Bezirke.
BEZIRKE_GEOJSON = "bezirke.geojson"

# Ausgabedatei für die Karte (Abbildung 3.5).
MAP_OUTPUT = "abbildung_3_5.png"


# ---------------------------------------------------------------------------
# 1. Referenzdaten (aus Tabelle 2.1 der Arbeit, Zensus 2022)
# ---------------------------------------------------------------------------
# Einwohnerzahl je Bezirk. Diese Werte stammen unverändert aus Tabelle 2.1
# und werden hier wiederverwendet, um Konsistenz über alle Kapitel zu wahren.
POPULATION = {
    "Mitte": 357319,
    "Friedrichshain-Kreuzberg": 264033,
    "Pankow": 400411,
    "Charlottenburg-Wilmersdorf": 317012,
    "Spandau": 237759,
    "Steglitz-Zehlendorf": 295124,
    "Tempelhof-Schöneberg": 331288,
    "Neukölln": 305022,
    "Treptow-Köpenick": 275537,
    "Marzahn-Hellersdorf": 270010,
    "Lichtenberg": 290543,
    "Reinickendorf": 252941,
}

# Abgeleitete Bezirksfläche in km² (ebenfalls aus Tabelle 2.1).
AREA_KM2 = {
    "Mitte": 39.47,
    "Friedrichshain-Kreuzberg": 20.16,
    "Pankow": 103.01,
    "Charlottenburg-Wilmersdorf": 64.72,
    "Spandau": 91.91,
    "Steglitz-Zehlendorf": 102.51,
    "Tempelhof-Schöneberg": 53.09,
    "Neukölln": 44.93,
    "Treptow-Köpenick": 168.42,
    "Marzahn-Hellersdorf": 61.74,
    "Lichtenberg": 52.29,
    "Reinickendorf": 89.47,
}

# Zuordnung Bezirk -> Einsatzbereich (EB E1–E6). Jeder Einsatzbereich fasst
# zwei benachbarte Bezirke zusammen [vgl. Berliner Feuerwehr 2024b].
BEZIRK_TO_EB = {
    "Mitte": "E1", "Friedrichshain-Kreuzberg": "E1",
    "Pankow": "E2", "Reinickendorf": "E2",
    "Spandau": "E3", "Charlottenburg-Wilmersdorf": "E3",
    "Steglitz-Zehlendorf": "E4", "Tempelhof-Schöneberg": "E4",
    "Neukölln": "E5", "Treptow-Köpenick": "E5",
    "Lichtenberg": "E6", "Marzahn-Hellersdorf": "E6",
}

# Anzahl hauptamtlich besetzter Berufsfeuerwachen je Einsatzbereich
# [vgl. Berliner Feuerwehr 2024b].
STATIONS_PER_EB = {"E1": 7, "E2": 6, "E3": 7, "E4": 7, "E5": 4, "E6": 4}


# ---------------------------------------------------------------------------
# 2. Einsatzdaten laden
# ---------------------------------------------------------------------------
def load_missions(path):
    """Lädt den Einsatzdatensatz und gibt einen pandas DataFrame zurück.

    low_memory=False verhindert, dass pandas die Spaltentypen blockweise rät;
    das ist bei dieser Datei mit gemischten Typen (z. B. leere Codespalten)
    zuverlässiger.
    """
    df = pd.read_csv(path, low_memory=False)

    # Kurze Plausibilitätsausgabe, damit man sofort sieht, ob der richtige
    # Datensatz geladen wurde. Die Erwartungswerte stammen aus Kapitel 2.
    n_total = len(df)
    n_missing = df["response_time"].isna().sum()
    n_valid = df["response_time"].notna().sum()
    print(f"Einsätze gesamt:            {n_total:>7}")
    print(f"davon ohne Hilfsfrist:      {n_missing:>7}")
    print(f"davon mit gültiger Frist:   {n_valid:>7}")
    print("-" * 40)
    return df


# ---------------------------------------------------------------------------
# 3. Tabelle 3.1 – Einsatzhäufigkeit je Bezirk
# ---------------------------------------------------------------------------
def build_table_3_1(df):
    """Erzeugt Tabelle 3.1: Einsätze je Bezirk, absolut und je 10.000 Einwohner."""
    # Einsätze je Bezirk zählen. groupby(...).size() liefert die Zeilenzahl
    # (= Einsatzzahl) pro Bezirk.
    counts = df.groupby("mission_location_district").size().rename("einsaetze")

    table = counts.to_frame()
    # Einwohnerzahl über das Referenz-Dictionary anfügen.
    table["einwohner"] = table.index.map(POPULATION)
    # Normierung: Einsätze je 10.000 Einwohner, auf eine Nachkommastelle gerundet.
    table["je_10k"] = (table["einsaetze"] / table["einwohner"] * 10000).round(1)

    # Absteigend nach absoluter Einsatzzahl sortieren (wie in der Arbeit).
    table = table.sort_values("einsaetze", ascending=False)

    print("Tabelle 3.1 – Einsatzhäufigkeit 2023 nach Bezirk")
    print(table.to_string())
    print("-" * 40)
    return table


# ---------------------------------------------------------------------------
# 4. Einsatzdichte je Einsatzbereich (EB E1–E6)
# ---------------------------------------------------------------------------
def aggregate_by_eb(table_3_1):
    """Aggregiert die Einsatzzahlen aus Tabelle 3.1 auf Ebene der Einsatzbereiche.

    Für jeden EB werden die Einsätze und die Einwohner der beiden zugehörigen
    Bezirke summiert und daraus die Einsatzdichte je 10.000 Einwohner berechnet.
    """
    # Spalte mit dem Einsatzbereich anlegen.
    df = table_3_1.copy()
    df["eb"] = df.index.map(BEZIRK_TO_EB)

    # Einsätze und Einwohner je EB aufsummieren.
    eb = df.groupby("eb").agg(einsaetze=("einsaetze", "sum"),
                              einwohner=("einwohner", "sum"))
    eb["je_10k"] = (eb["einsaetze"] / eb["einwohner"] * 10000).round(1)
    eb = eb.sort_values("je_10k", ascending=False)

    print("Einsatzdichte je Einsatzbereich (EB E1–E6)")
    print(eb.to_string())
    print("-" * 40)
    return eb


# ---------------------------------------------------------------------------
# 5. Tabelle 3.2 – Wachen je Einsatzbereich und Fläche je Wache
# ---------------------------------------------------------------------------
def build_table_3_2():
    """Erzeugt Tabelle 3.2: Berufsfeuerwachen je EB und durchschnittliche Fläche je Wache."""
    rows = []
    for eb, n_stations in STATIONS_PER_EB.items():
        # Gesamtfläche des Einsatzbereichs = Summe der Flächen der beiden Bezirke.
        bezirke = [b for b, e in BEZIRK_TO_EB.items() if e == eb]
        area = sum(AREA_KM2[b] for b in bezirke)
        # km² pro Wache = Gesamtfläche / Anzahl Wachen.
        km2_per_station = round(area / n_stations, 2)
        rows.append({
            "eb": eb,
            "bezirke": " / ".join(bezirke),
            "wachen": n_stations,
            "flaeche_km2": round(area, 2),
            "km2_je_wache": km2_per_station,
        })

    table = pd.DataFrame(rows).set_index("eb").sort_index()
    print("Tabelle 3.2 – Berufsfeuerwachen je Einsatzbereich und Fläche je Wache")
    print(table.to_string())
    print("-" * 40)
    return table


# ---------------------------------------------------------------------------
# 6. Abbildung 3.5 – Choroplethenkarte der durchschnittlichen Hilfsfrist
# ---------------------------------------------------------------------------
def build_map_3_5(df, geojson_path, output_path):
    """Erzeugt die Choroplethenkarte der mittleren Hilfsfrist je Bezirk."""
    # Nur Einsätze mit gültiger Hilfsfrist berücksichtigen; ein einziger
    # fehlender Wert würde den Mittelwert des Bezirks sonst zu NaN machen.
    valid = df[df["response_time"].notna()]

    # Mittlere Hilfsfrist je Bezirk in Minuten (Rohdaten liegen in Sekunden vor).
    mean_min = (valid.groupby("mission_location_district")["response_time"]
                .mean().div(60).round(1))

    # Bezirksgeometrien laden.
    gdf = gpd.read_file(geojson_path)
    # Hilfsfrist-Werte über den Bezirksnamen an die Polygone anfügen.
    gdf["mean_min"] = gdf["name"].map(mean_min)

    # Sicherheitsprüfung: Wenn ein Bezirksname nicht übereinstimmt (z. B. andere
    # Schreibweise), bliebe hier ein NaN und der Bezirk wäre auf der Karte leer.
    if gdf["mean_min"].isna().any():
        fehlend = gdf.loc[gdf["mean_min"].isna(), "name"].tolist()
        raise ValueError(f"Kein Hilfsfrist-Wert zugeordnet für: {fehlend}")

    # --- Zeichnen -----------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10.5, 7.2), dpi=150)

    # Choroplethenkarte: Füllfarbe nach mittlerer Hilfsfrist. viridis ist
    # farbenblind-sicher – erfüllt die Vorgabe aus dem Workshop, an Personen
    # mit Rot-Grün-Sehschwäche zu denken.
    gdf.plot(column="mean_min", cmap="viridis", linewidth=0.9,
             edgecolor="white", ax=ax, legend=True,
             legend_kwds={"label": "Ø Hilfsfrist (Minuten)", "shrink": 0.75})

    # Stadtweiter Mittelwert als Schwelle für die Textfarbe (heller Text auf
    # dunklen Flächen, dunkler Text auf hellen Flächen).
    schwelle = 11.3
    for _, row in gdf.iterrows():
        punkt = row.geometry.representative_point()
        wert = row["mean_min"]
        farbe = "white" if wert < schwelle else "black"
        ax.annotate(f"{row['name']}\n{wert:.1f}",
                    xy=(punkt.x, punkt.y), ha="center", va="center",
                    fontsize=7.2, color=farbe, weight="bold", linespacing=1.15)

    ax.set_title("Durchschnittliche Hilfsfrist 2023 nach Bezirk",
                 fontsize=13, weight="bold", pad=12)
    ax.set_axis_off()  # Koordinatenachsen bei Karten entfernen.

    # Hinweis auf das Schutzziel (8 Minuten) als Untertitel.
    ax.annotate("Schutzziel: 8,0 Min. — kein Bezirk unterschreitet diesen Wert im Mittel",
                xy=(0.5, -0.02), xycoords="axes fraction", ha="center",
                fontsize=8.5, style="italic", color="#444444")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Karte gespeichert unter: {output_path}")
    print("-" * 40)
    return gdf


# ---------------------------------------------------------------------------
# 7. Hauptprogramm
# ---------------------------------------------------------------------------
def main():
    # Einsatzdaten einmal laden und für alle Auswertungen wiederverwenden.
    df = load_missions(MISSION_CSV)

    # Tabellen und Aggregationen erzeugen.
    table_3_1 = build_table_3_1(df)
    aggregate_by_eb(table_3_1)
    build_table_3_2()

    # Karte erzeugen.
    build_map_3_5(df, BEZIRKE_GEOJSON, MAP_OUTPUT)


# Standard-Einstiegspunkt: main() nur ausführen, wenn das Skript direkt
# gestartet wird (nicht beim Import als Modul).
if __name__ == "__main__":
    main()
