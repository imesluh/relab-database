from apscheduler.schedulers.gevent import GeventScheduler
import os
basedir = os.path.abspath(os.path.dirname(__file__))
from . import user_classes#importlib.util
#spec = importlib.util.spec_from_file_location("user_classes", basedir+"/db/user_classes.py")
#user_classes = importlib.util.module_from_spec(spec)
#spec.loader.exec_module(user_classes)

#from database_fcn import connection
import datetime

minute = int(datetime.datetime.now().strftime('%M'))
if 29 <= minute <=58:
    merker=2
else:
    merker=1


def clean_db(conn):
    global merker
    minute = int(datetime.datetime.now().strftime('%M'))
    if 29 <= minute <=58 and merker ==1:
        start = datetime.datetime.strptime((datetime.datetime.now().strftime("%Y %m %d %H") + ' 30'), "%Y %m %d %H %M")
        if minute == 55:
            merker=2
        merker = conn.check_reservation(start, merker)
    elif merker ==2 and (minute==59 or minute<29):
        if minute >30:
            start = datetime.datetime.strptime((datetime.datetime.now().strftime("%Y %m %d %H") + ' 00'), "%Y %m %d %H %M")+ datetime.timedelta(hours=1)
        else:
            start = datetime.datetime.strptime((datetime.datetime.now().strftime("%Y %m %d %H") + ' 00'), "%Y %m %d %H %M")
        if minute == 25:
            merker=1
        merker = conn.check_reservation(start, merker)
