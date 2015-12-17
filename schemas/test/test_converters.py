import json, os, unittest

LOCAL = os.path.dirname(__file__)
SAMPLE_PING_PATH = os.path.join(LOCAL, 'sample_v4_ping.json')
BASE_SET_PATH = os.path.join(LOCAL, '..', 'base_set.json')
CRASH_SUMMARY_PATH = os.path.join(LOCAL, '..', 'crash_summary.json')
