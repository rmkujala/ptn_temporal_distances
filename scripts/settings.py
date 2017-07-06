# -*- coding: latin-1 -*-
import os
import pytz

RESULTS_DIRECTORY = "../results/"
DATA_DIRECTORY = "../data/"
FIGS_DIRECTORY = "../figs/"

IMPORTED_DATABASE_PATH = DATA_DIRECTORY + "main.sqlite"

RAW_GTFS_ZIP_PATH =  os.path.join(DATA_DIRECTORY, "raw", "gtfs.zip")

HELSINKI_DATA_BASEDIR = os.path.join(DATA_DIRECTORY, "helsinki/2016-09-28/")
HELSINKI_NODES_FNAME = HELSINKI_DATA_BASEDIR + "main.day.nodes.csv"
HELSINKI_TRANSIT_CONNECTIONS_FNAME = os.path.join(HELSINKI_DATA_BASEDIR, "main.day.temporal_network.csv")
HELSINKI_TRANSFERS_FNAME = os.path.join(HELSINKI_DATA_BASEDIR, "main.day.transfers.csv")


DEFAULT_TILES = "CartoDB positron"
DARK_TILES = "CartoDB dark_matter"

DAY_START = 1475438400 + 3600
DAY_END = DAY_START + 24 * 3600

ROUTING_START_TIME_DEP = DAY_START + 8 * 3600  # 07:00 AM

ANALYSIS_START_TIME_DEP = ROUTING_START_TIME_DEP
ANALYSIS_END_TIME_DEP = ROUTING_START_TIME_DEP + 1 * 3600

ROUTING_END_TIME_DEP = ROUTING_START_TIME_DEP + 3 * 3600

# AALTO_STOP_ID = 3363
# # 3363,2222211,E2229,Alvar Aallon puisto,Otaniementie,60.183984,24.829145,,0,0,3363
#
# ITAKESKUS_STOP_ID = 2179
# # 2179,1453601,0023,Itäkeskus,Itäkeskus,60.209989,25.077984,7534.0,0,0,7534
#
# MUNKKIVUORI_STOP_ID = 1161
# # 1161,1304137,1396,Munkkivuori,Huopalahdentie,60.20595,24.87998,,0,2,1161

TIMEZONE = pytz.timezone("Europe/Helsinki")

# from jinja2 import defaults
# defaults.LSTRIP_BLOCKS = True
# defaults.KEEP_TRAILING_NEWLINE = False
# defaults.TRIM_BLOCKS = True

AALTO_UNIVERSITY_LAT_LON = (60.185944, 24.826750)
ITAKESKUS_LAT_LON = (60.211942, 25.082946)
MUNKKIVUORI_LAT_LON = (60.206037, 24.877290)

AALTO_UNIVERSITY_ID = "ADDED_AALTO_UNIVERSITY"
ITAKESKUS_ID = "ADDED_ITAKESKUS_UNIVERSITY" # Should have been "ADDED_ITAKESKUS" (There is no University in Itakeskus..)
MUNKKIVUORI_ID = "ADDED_MUNKKIVUORI"

SWIMMING_HALL_ID_PREFIX = "SWIMMING_HALL_"

EXTRA_LOCATIONS = [
    {'id': AALTO_UNIVERSITY_ID,
     'lat': AALTO_UNIVERSITY_LAT_LON[0],
     'lon': AALTO_UNIVERSITY_LAT_LON[1]},
    {'id': ITAKESKUS_ID,
     'lat': ITAKESKUS_LAT_LON[0],
     'lon': ITAKESKUS_LAT_LON[1]},
    {'id': MUNKKIVUORI_ID,
     'lat': MUNKKIVUORI_LAT_LON[0],
     'lon': MUNKKIVUORI_LAT_LON[1]}
]

LONG_DISTANCE_STOPS = [

]


def get_stop_I_by_stop_id(stop_id):
    from gtfspy.gtfs import GTFS
    g = GTFS(IMPORTED_DATABASE_PATH)
    query = "SELECT stop_I FROM stops WHERE stop_id='" + str(stop_id) + "';"
    print(stop_id)
    stop_I = g.execute_custom_query(query).fetchone()[0]
    return stop_I

def get_swimming_hall_stop_Is():
    from gtfspy.gtfs import GTFS
    g = GTFS(IMPORTED_DATABASE_PATH)
    query = 'SELECT stop_I FROM stops WHERE SUBSTR(stop_id, 0, 7)="SWIMMI";'
    stop_Is = [el[0] for el in g.execute_custom_query(query).fetchall()]
    return stop_Is

import matplotlib as mpl
mpl.style.use('classic')

import smopy
smopy.TILE_SERVER = "https://cartodb-basemaps-1.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png"

