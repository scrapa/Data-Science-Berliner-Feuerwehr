# =========================================================================
# CHAPTER 2: DATA PREPARATION & FEATURE ENGINEERING (PERSON 2)
# Author: Adam Kefi
# =========================================================================

library(tidyverse)
library(sf)

print("Starting Data Preparation (Person 2)...")

# =========================================================================
# 2.1 READ DATA SOURCES
# =========================================================================

# 1. Census Data
zensus_raw <- read_csv2("data/Zensus_Datenportal.csv") 

# 2. District Centers (Our new manual CSV!)
districts_raw <- read_csv("data/bezirke_centroids.csv", show_col_types = FALSE)
districts_sf <- districts_raw |>
  st_as_sf(coords = c("lon", "lat"), crs = 4326)

# 3. Fire Stations (The good CSV you found!)
stations_raw <- read_csv("data/feuerwehr_a_feuerwehr_standorte_WGS84.csv", show_col_types = FALSE)
stations_sf <- stations_raw |>
  st_as_sf(coords = c("lon", "lat"), crs = 4326)

# 4. Incidents Data (512,885 rows)
incidents_raw <- read_csv("data/mission_data_set_open_data_2023.csv", show_col_types = FALSE)


# =========================================================================
# 2.2 & 2.3 FEATURE ENGINEERING: POPULATION DENSITY
# =========================================================================

pop <- zensus_raw |>
  filter(Ausprägung == "15.05.2022") |>
  select(District = Gebietseinheit, Population = Werte)

dens <- zensus_raw |>
  filter(Ausprägung == "Einwohnerdichte") |>
  select(District = Gebietseinheit, Density = Werte)

districts_features <- pop |>
  left_join(dens, by = "District") |>
  mutate(
    Area_km2 = round(Population / Density, 2)
  )


# =========================================================================
# 2.2 & 2.3 FEATURE ENGINEERING: STRAIGHT-LINE DISTANCE
# =========================================================================

# Transform both layers to the metric system (EPSG:25833 - meters)
districts_proj <- st_transform(districts_sf, crs = 25833)
stations_proj  <- st_transform(stations_sf, crs = 25833)

# Measure the exact distance to the nearest station
districts_distance <- districts_proj |>
  mutate(
    nearest_station_idx = st_nearest_feature(geometry, stations_proj),
    Distance_to_Station_m = as.numeric(st_distance(geometry, stations_proj[nearest_station_idx, ], by_element = TRUE)),
    Distance_to_Station_m = round(Distance_to_Station_m, 0)
  ) |>
  select(District, Distance_to_Station_m) |>
  st_drop_geometry()


# =========================================================================
# FINAL MERGE AND TEAM EXPORT
# =========================================================================

# Attach all features to the 512,885 incidents
incidents_final <- incidents_raw |>
  left_join(districts_distance, by = c("mission_location_district" = "District")) |>
  left_join(districts_features, by = c("mission_location_district" = "District"))

# Export the clean dataset for your team members
write_csv(incidents_final, "data/incidents_2023_cleaned_TEAM.csv")

# --- RESULTS ---
print("--- DATA PIPELINE COMPLETE ---")
print("Sanity Check for Distance (Meters):")
summary(incidents_final$Distance_to_Station_m)