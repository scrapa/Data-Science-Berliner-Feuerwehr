# =========================================================================
# KAPITEL 3.1: ZEITLICHE MUSTER — PERSON 3
# Seminararbeit: Faktoren der Hilfsfristen bei der Berliner Feuerwehr
# HTW Berlin | Einführung Data Science | SoSe 2026
# =========================================================================
# Voraussetzung: feuerwehr_clean.csv liegt im Ordner data/
#                (bereinigter Datensatz aus Kapitel 2 / Person 2)
# Ausführen:     python kapitel_3_1.py
#
# HINWEIS: Die öffentlichen Daten enthalten nur das DATUM, keine Uhrzeit.
#          Deshalb ist eine tageszeitliche Analyse (nach Stunde) nicht
#          möglich. Dieses Skript analysiert wöchentliche und saisonale
#          Muster. Siehe Kommentar in Kapitel 3.1.1.
#
# HINWEIS ZUR DARSTELLUNG: Die Grafiken tragen bewusst KEINEN Titel im Bild.
#          Die Beschriftung (Abbildung 3.x) erfolgt ausschließlich als
#          Bildunterschrift im Text der Seminararbeit.
# =========================================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
from matplotlib.patches import Patch

os.makedirs("output", exist_ok=True)

# -------------------------------------------------------------------------
# EINHEITLICHES DESIGN
# -------------------------------------------------------------------------
plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "axes.labelsize":    12,
    "xtick.labelsize":   11,
    "ytick.labelsize":   11,
    "figure.dpi":        200,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})
ROT         = "#C0392B"
GRAU_HELL   = "#D5D8DC"
GRAU_DUNKEL = "#5D6D7E"
BLAU        = "#2471A3"

WOCHENTAGE_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                 "Freitag", "Samstag", "Sonntag"]
MONATE_DE = {1:"Jan", 2:"Feb", 3:"Mär", 4:"Apr", 5:"Mai", 6:"Jun",
             7:"Jul", 8:"Aug", 9:"Sep", 10:"Okt", 11:"Nov", 12:"Dez"}

# =========================================================================
# DATEN LADEN
# =========================================================================
print("Lade feuerwehr_clean.csv ...")
df = pd.read_csv("data/feuerwehr_clean.csv", low_memory=False)
df["mission_date"] = pd.to_datetime(df["mission_date"], errors="coerce")
print(f"  -> {len(df):,} Einsätze")

# Zeitfeatures ableiten
df["Wochentag"]   = df["mission_date"].dt.dayofweek       # 0=Mo, 6=So
df["Monat"]       = df["mission_date"].dt.month
df["Jahreswoche"] = df["mission_date"].dt.isocalendar().week.astype(int)
df["response_min"]= df["response_time"] / 60
df["Monat_Name"]  = df["Monat"].map(MONATE_DE)


# =========================================================================
# ABBILDUNG 3.1: Einsatzvolumen nach Wochentag   (Kapitel 3.1.1)
# =========================================================================
print("Erstelle Abb. 3.1 ...")
wt_counts = df.groupby("Wochentag").size().reset_index(name="Anzahl")
wt_counts["Tag"] = [WOCHENTAGE_DE[i] for i in wt_counts["Wochentag"]]
farben = [ROT if i >= 5 else GRAU_DUNKEL for i in wt_counts["Wochentag"]]

fig, ax = plt.subplots(figsize=(10, 5.2))
bars = ax.bar(wt_counts["Tag"], wt_counts["Anzahl"],
              color=farben, edgecolor="white", width=0.65)
for bar, val in zip(bars, wt_counts["Anzahl"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 400,
            f"{val:,.0f}".replace(",", "."), ha="center", va="bottom", fontsize=9.5)
ax.set_ylabel("Anzahl Einsätze")
ax.set_ylim(0, wt_counts["Anzahl"].max() * 1.15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
# Legende oben AUSSERHALB, damit sie keine Balken überlappt
ax.legend(handles=[Patch(facecolor=GRAU_DUNKEL, label="Werktag (Mo–Fr)"),
                   Patch(facecolor=ROT,          label="Wochenende (Sa–So)")],
          frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.09), ncol=2)
plt.tight_layout()
plt.savefig("output/abb1_einsaetze_wochentag.png", bbox_inches="tight")
plt.close()


# =========================================================================
# ABBILDUNG 3.2: Hilfsfrist nach Wochentag   (Kapitel 3.1.1)
# =========================================================================
print("Erstelle Abb. 3.2 ...")
wt_stats = df.groupby("Wochentag")["response_min"].agg(["mean", "median"]).reset_index()
wt_stats["Tag"] = [WOCHENTAGE_DE[i] for i in wt_stats["Wochentag"]]

fig, ax = plt.subplots(figsize=(10, 5.2))
ax.bar(wt_stats["Tag"], wt_stats["mean"],
       color=GRAU_HELL, edgecolor=GRAU_DUNKEL, width=0.5, label="Mittelwert")
ax.plot(wt_stats["Tag"], wt_stats["median"],
        color=ROT, linewidth=2.2, marker="o", markersize=7, label="Median")
ax.axhline(8, color="black", linewidth=1.2, linestyle=":", alpha=0.7)
ax.text(6.55, 8.15, "8 Min. (Schutzziel)", fontsize=9, color="black", ha="right")
ax.set_ylabel("Hilfsfrist (Minuten)")
ax.set_ylim(0, 13)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.09), ncol=2)
plt.tight_layout()
plt.savefig("output/abb2_hilfsfrist_wochentag.png", bbox_inches="tight")
plt.close()


# =========================================================================
# ABBILDUNG 3.3: Monatsverlauf — Volumen + Hilfsfrist   (Kapitel 3.1.2)
# =========================================================================
print("Erstelle Abb. 3.3 ...")
monat_stats = (df.groupby("Monat")
                 .agg(Anzahl=("response_min", "count"),
                      Hilfsfrist_min=("response_min", "mean"))
                 .reset_index())
monat_stats["Monat_Name"] = monat_stats["Monat"].map(MONATE_DE)

fig, ax1 = plt.subplots(figsize=(11, 5.2))
ax2 = ax1.twinx()
ax1.bar(monat_stats["Monat_Name"], monat_stats["Anzahl"],
        color=GRAU_HELL, edgecolor=GRAU_DUNKEL, width=0.62, label="Einsatzanzahl")
ax2.plot(monat_stats["Monat_Name"], monat_stats["Hilfsfrist_min"],
         color=ROT, linewidth=2.5, marker="o", markersize=6, label="Ø Hilfsfrist")
ax2.axhline(8, color="black", linewidth=1.0, linestyle=":", alpha=0.6)
ax2.text(11.5, 8.12, "8 Min.", fontsize=9, color="black")
ax1.set_ylabel("Anzahl Einsätze", color=GRAU_DUNKEL)
ax2.set_ylabel("Ø Hilfsfrist (Min.)", color=ROT)
ax1.tick_params(axis="y", colors=GRAU_DUNKEL)
ax2.tick_params(axis="y", colors=ROT)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
ax2.set_ylim(0, 13)
l1, la1 = ax1.get_legend_handles_labels()
l2, la2 = ax2.get_legend_handles_labels()
# Legende oben AUSSERHALB
ax1.legend(l1 + l2, la1 + la2, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.10), ncol=2)
plt.tight_layout()
plt.savefig("output/abb3_monatsverlauf.png", bbox_inches="tight")
plt.close()


# =========================================================================
# ABBILDUNG 3.4: Wöchentliches Volumen — Silvester-Ausreißer  (Kapitel 3.1.2)
# =========================================================================
print("Erstelle Abb. 3.4 ...")
wochen_stats = df.groupby("Jahreswoche").size().reset_index(name="Anzahl")
silvester_kws = [1, 52]
farben_w = [ROT if w in silvester_kws else BLAU for w in wochen_stats["Jahreswoche"]]

fig, ax = plt.subplots(figsize=(13, 5.2))
ax.bar(wochen_stats["Jahreswoche"], wochen_stats["Anzahl"],
       color=farben_w, edgecolor="none", width=0.85)
mittelwert = wochen_stats["Anzahl"].mean()
ax.axhline(mittelwert, color=GRAU_DUNKEL, linewidth=1.5, linestyle="--")
ax.text(53.5, mittelwert + 60, f"Ø {mittelwert:,.0f}".replace(",", "."),
        fontsize=9, color=GRAU_DUNKEL)
for kw in silvester_kws:
    row = wochen_stats[wochen_stats["Jahreswoche"] == kw]
    if not row.empty:
        y = row["Anzahl"].values[0]
        ax.annotate(f"KW {kw}\n(Silvester)", xy=(kw, y),
                    xytext=(kw + 3.5, y + 400),
                    arrowprops=dict(arrowstyle="->", color="black", lw=1.3),
                    fontsize=9)
ax.set_xlabel("Kalenderwoche")
ax.set_ylabel("Anzahl Einsätze")
ax.set_xlim(0.5, 55)
ax.set_ylim(0, wochen_stats["Anzahl"].max() * 1.12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
ax.legend(handles=[Patch(facecolor=BLAU, label="Normalwochen"),
                   Patch(facecolor=ROT,  label="Silvester / Jahreswechsel")],
          frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.09), ncol=2)
plt.tight_layout()
plt.savefig("output/abb4_silvester_ausreisser.png", bbox_inches="tight")
plt.close()


# =========================================================================
# KENNZAHLEN für den Text
# =========================================================================
print("\n" + "=" * 60)
print("KENNZAHLEN FÜR DEN SEMINARARBEITSTEXT")
print("=" * 60)
print(f"\nEinsätze gesamt (bereinigt): {len(df):,}")

wt = df.groupby("Wochentag").size()
print(f"Meiste Einsätze:    {WOCHENTAGE_DE[wt.idxmax()]} ({wt.max():,})")
print(f"Wenigste Einsätze:  {WOCHENTAGE_DE[wt.idxmin()]} ({wt.min():,})")

we = df[df["Wochentag"] >= 5].groupby("Wochentag").size().mean()
wk = df[df["Wochentag"] <  5].groupby("Wochentag").size().mean()
print(f"Ø Werktag: {wk:,.0f}  |  Ø Wochenendtag: {we:,.0f}")

mt = df.groupby("Monat").size()
print(f"Stärkster Monat:    {MONATE_DE[mt.idxmax()]} ({mt.max():,})")
print(f"Schwächster Monat:  {MONATE_DE[mt.idxmin()]} ({mt.min():,})")

ws = df.groupby("Wochentag")["response_min"].mean()
print(f"Längste Ø Hilfsfrist:  {ws.max():.1f} Min. ({WOCHENTAGE_DE[ws.idxmax()]})")
print(f"Kürzeste Ø Hilfsfrist: {ws.min():.1f} Min. ({WOCHENTAGE_DE[ws.idxmin()]})")

kw1  = wochen_stats[wochen_stats["Jahreswoche"] == 1]["Anzahl"].values
kw52 = wochen_stats[wochen_stats["Jahreswoche"] == 52]["Anzahl"].values
if len(kw1)  > 0: print(f"Einsätze KW 1  (Neujahr):   {kw1[0]:,}")
if len(kw52) > 0: print(f"Einsätze KW 52 (Silvester): {kw52[0]:,}")
print(f"Ø Wocheneinsätze gesamt:    {wochen_stats['Anzahl'].mean():,.0f}")

print("\n" + "=" * 60)
print("FERTIG — 4 Abbildungen im Ordner output/")
print("=" * 60)