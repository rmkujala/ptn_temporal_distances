# -*- coding: latin-1 -*-
import os
import pytz

RESULTS_DIRECTORY = "../results/"
FIGS_DIRECTORY = "../figs/"

HELSINKI_DATA_BASEDIR = "../data/helsinki/2016-09-28/"
HELSINKI_NODES_FNAME = HELSINKI_DATA_BASEDIR + "main.day.nodes.csv"
HELSINKI_TRANSIT_CONNECTIONS_FNAME = os.path.join(HELSINKI_DATA_BASEDIR, "main.day.temporal_network.csv")

DEFAULT_TILES = "CartoDB positron"
DARK_TILES = "CartoDB dark_matter"

DAY_START = 1475438400 + 3600
DAY_END = DAY_START + 24 * 3600

ROUTING_START_TIME_DEP = DAY_START + 8 * 3600  # 07:00 AM

ANALYSIS_START_TIME_DEP = ROUTING_START_TIME_DEP
ANALYSIS_END_TIME_DEP = ROUTING_START_TIME_DEP + 1 * 3600

ROUTING_END_TIME_DEP = ROUTING_START_TIME_DEP + 3 * 3600

AALTO_STOP_ID = 3363
# 3363,2222211,E2229,Alvar Aallon puisto,Otaniementie,60.183984,24.829145,,0,0,3363

ITAKESKUS_STOP_ID = 2179
# 2179,1453601,0023,Itškeskus,Itškeskus,60.209989,25.077984,7534.0,0,0,7534

MUNKKIVUORI_STOP_ID = 1161
# 1161,1304137,1396,Munkkivuori,Huopalahdentie,60.20595,24.87998,,0,2,1161

TIMEZONE = pytz.timezone("Europe/Helsinki")

from jinja2 import defaults
defaults.LSTRIP_BLOCKS = True
defaults.KEEP_TRAILING_NEWLINE = False
defaults.TRIM_BLOCKS = True
