from src.eams_crawler.lib.EAMS import EAMSSession, EAMSParser
from src.eams_crawler.lib.OA import OASession, SportSystem

from src.eams_crawler.database import connect
from src.eams_crawler.database import insert
import requests

import time

session = OASession("20181131234", "p19991025")
if session.login():
    s = EAMSParser(session)
    print(s.get_stuid())


