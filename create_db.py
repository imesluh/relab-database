"""
Das Skript erstellt die Datenbanken neu. Es wird durch alle Datenbanken (MechSys, RobotikI und RobotikII) iteriert und jedesmal
gefragt, ob sie entsprechend des Modells in user_classes neu erstellt werden soll. Es werden dann auch die Passwort-Dateien (htpasswd
für die Kennwortüberprüfung und passwd... zur Speicherung der Kennwörter im Klarnamen)
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import create_database, drop_database, drop_database, database_exists
import user_classes
import os
import sys
sys.path.insert(0, '/var/www/server/app')
import get_passwords as get_pw

## Das Skript erstellt die Datenbanken neu. Es wird durch alle Datenbanken (MechSys, RobotikI und RobotikII) iteriert und jedesmal
## gefragt, ob sie entsprechend des Modells in user_classes neu erstellt werden soll. Es werden dann auch die Passwort-Dateien (htpasswd
## für die Kennwortüberprüfung und passwd... zur Speicherung der Kennwörter im Klarnamen)

pw_sql = get_pw.password_sql()
ip_server = get_pw.get_ip('SERVER_IP')
## Drop all in MechSys und erstelle alles neu (und leer)
engine = create_engine("mysql+pymysql://relab:" + pw_sql + "@" + ip_server + ":3306/MechSys")  # Access the DB Engine
if database_exists(engine.url):
    ans = input('Die Datenbank MechSys existiert schon. Soll sie wirklich gelöscht und leer neu erstellt werden? [y=yes, n=no]: ')
    if ans == 'y':
        drop_database(engine.url)
        create_database(engine.url)
        Base = declarative_base()
        User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
        Base.metadata.create_all(engine)

        os.system("> /etc/nginx/.htpasswd_MechSys")
        os.system("> /etc/nginx/.htpasswd_MechSys_admin")
        os.system("> /var/www/server/db_server/passwdMechSys.txt")
        print('MechSys-Datenbank gelöscht und neu erstellt.')
    else:
        print('MechSys-Datenbank nicht neu erstellt.')
else:
    drop_database(engine.url)
    create_database(engine.url)
    Base = declarative_base()
    User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
    Base.metadata.create_all(engine)
    os.system("> /etc/nginx/.htpasswd_MechSys")
    os.system("> /etc/nginx/.htpasswd_MechSys_admin")
    os.system("> /var/www/server/db_server/passwdMechSys.txt")
    print('MechSys-Datenbank erstellt.')


## Drop all in RobotikI und erstelle alles neu (und leer)
engine = create_engine("mysql+pymysql://relab:" + pw_sql + "@" + ip_server + ":3306/RobotikI")  # Access the DB Engine
if database_exists(engine.url):
    ans = input('Die Datenbank RobotikI existiert schon. Soll sie wirklich gelöscht und leer neu erstellt werden? [y=yes, n=no]: ')
    if ans == 'y':
        drop_database(engine.url)
        create_database(engine.url)
        Base = declarative_base()
        User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
        Base.metadata.create_all(engine)
        os.system("> /etc/nginx/.htpasswd_RobotikI")
        os.system("> /etc/nginx/.htpasswd_RobotikI_admin")
        os.system("> /var/www/server/db_server/passwdRobotikI.txt")
        print('RobotikI-Datenbank gelöscht und neu erstellt.')
    else:
        print('RobotikI-Datenbank nicht neu erstellt.')
else:
    create_database(engine.url)
    Base = declarative_base()
    User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
    Base.metadata.create_all(engine)
    os.system("> /etc/nginx/.htpasswd_RobotikI")
    os.system("> /etc/nginx/.htpasswd_RobotikI_admin")
    os.system("> /var/www/server/db_server/passwdRobotikI.txt")
    print('RobotikI-Datenbank erstellt.')

## Drop all in RobotikII und erstelle alles neu (und leer)
engine = create_engine("mysql+pymysql://relab:" + pw_sql + "@" + ip_server + ":3306/RobotikII")  # Access the DB Engine
if database_exists(engine.url):
    ans = input('Die Datenbank RobotikII existiert schon. Soll sie wirklich gelöscht und leer neu erstellt werden? [y=yes, n=no]: ')
    if ans == 'y':
        drop_database(engine.url)
        create_database(engine.url)
        Base = declarative_base()
        User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
        Base.metadata.create_all(engine)
        os.system("> /etc/nginx/.htpasswd_RobotikII")
        os.system("> /etc/nginx/.htpasswd_RobotikII_admin")
        print('RobotikII-Datenbank gelöscht und neu erstellt.')
        os.system("> /var/www/server/db_server/passwdRobotikII.txt")
    else:
        print('RobotikII-Datenbank nicht neu erstellt.')
else:
    create_database(engine.url)
    Base = declarative_base()
    User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
    Base.metadata.create_all(engine)
    os.system("> /etc/nginx/.htpasswd_RobotikII")
    os.system("> /etc/nginx/.htpasswd_RobotikII_admin")
    os.system("> /var/www/server/db_server/passwdRobotikII.txt")
    print('RobotikII-Datenbank erstellt.')
