import requests
import pandas as pd
import json
import geopandas as gpd
from sodapy import Socrata
import time

#start timer to see how long program takes
tic = time.perf_counter()

socrata_domain = "data.lacity.org"
id = "d5tf-ez2w"
client = Socrata(socrata_domain, "jEqnFj2BvLJwBvLPURiPkUNOh ", timeout=100) #app id token from socrata profile 

#this querys the db for all crashes since 1/1/2022 that have either a bike or pedestrian involved
#usually returns around 2k crashes/year? so the limit of 100k should work as long as we need
#modify this to start in 2023 after testing is done
query = """
SELECT
  *
WHERE
  ((`date_occ` > "2019-01-01T00:00:00" :: floating_timestamp)
     AND contains(`mocodes`, "3003"))
    OR ((`date_occ` > "2019-01-01T00:00:00" :: floating_timestamp)
          AND contains(`mocodes`, "3008"))
LIMIT 
    100000
"""

#query db
results = client.get(id, query=query)
results_df = pd.DataFrame.from_records(results)

print(f"Collisions downloaded: {len(results_df)}")

#turn into gdf and select only points within cd4
gdf = gpd.GeoDataFrame(results_df, geometry = gpd.points_from_xy(results_df.location_1.str['longitude'], results_df.location_1.str['latitude']))
cd4 = gpd.read_file("CD4.geojson")
gdf = gdf.set_crs(epsg=4326)
#for some reason this produces an error message but still works? 
cd4_collisions = gpd.sjoin(gdf, cd4, predicate='within')
print(f"Collisions within CD4: {len(cd4_collisions)}")

#isolate year from timestamp to deal with multiple years (2023, 2024, etc)
#this is unnecessary for now but will be useful in future
cd4_collisions['year'] = cd4_collisions.date_occ.str.slice(start = 0, stop = 4)
cd4_collisions.year

#rename columns to match old style (used in frontend leaflet code)
cd4_collisions = cd4_collisions.rename(columns={"date_occ": "Date Occurred", "time_occ": "Time Occurred", "vict_age": "Victim Age", "vict_sex": "Victim Sex", "mocodes": "MO Codes"})

#split df into different years and save the corresponding dfs into separate files
split = list(cd4_collisions.groupby("year"))
print(f"Years of data present: {len(split)}")
for df in split: 
    name = "crashes/"+df[0]+"collisions.geojson"
    df[1].to_file(name, driver = "GeoJSON")

#end timer
toc = time.perf_counter()

print(f"Downloaded, processed, and saved updated collision data in {toc - tic:0.3f} seconds")

