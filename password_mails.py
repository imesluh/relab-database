"""Die Funktion schickt die Anmeldedaten (zufällig generierte Passwörter) an die Studierenden. Hierzu muss die Firewall deaktiviert sein (bzw. der entsprechende Port freigeschaltet werden."""
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import user_classes

import json
import datetime
from email.mime.text import MIMEText
from email.header import Header
import subprocess
import smtplib
import time
import string
import random
import os

import sys
sys.path.insert(0, '/var/www/server/app')
import get_passwords as get_pw

## Die Funktion schickt die Anmeldedaten (zufällig generierte Passwörter) an die Studierenden. Hierzu muss
## die Firewall deaktiviert sein (bzw. der entsprechende Port freigeschaltet werden.

## Aufruf: python3 password_mails.py --lecture MechSys
## Aufruf: python3 password_mails.py --lecture RobotikI

pw_sql = get_pw.password_sql()
pw_mail = get_pw.password_mail()
pw_defaultUsers = get_pw.password_db_defaultUsers()
ip_server = get_pw.get_ip('SERVER_IP')


def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

def main(lecture):
    Absender = 'relab@imes.uni-hannover.de'
    Passwort = pw_mail
    smtpserver = smtplib.SMTP('email.uni-hannover.de', 587)
    print('Verbindung zum Mail-Server wird aufgebaut.')
    smtpserver.ehlo()
    smtpserver.starttls()

    # In Account einloggen
    print('Login-Versuch wird gestartet.')
    smtpserver.login(Absender, Passwort)
    print('Login erfolgreich. Es können Daten gesendet werden.')

    first = True

    basedir = os.path.abspath(os.path.dirname(__file__))

    engine = create_engine("mysql+pymysql://relab:" + pw_sql + "@" + ip_server + ":3306/" + lecture)
    Base = declarative_base()
    User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
    Base.metadata.create_all(engine)

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    users = session.query(User).all()
    i_mail = 0
    for user in users:
        if not user.password:
            if not user.last_name == 'imes':
                password =id_generator()
            else:
                password = pw_defaultUsers
            if lecture == 'MechSys':
                url = 'https://relab.imes.uni-hannover.de/MechSys'
                pwdFileName = "passwdMechSys.txt"
                htpwdFileName = "/etc/nginx/.htpasswd_MechSys"
            elif lecture == 'RobotikI':
                url = 'https://relab.imes.uni-hannover.de/RobotikI'
                pwdFileName = "passwdRobotikI.txt"
                htpwdFileName = "/etc/nginx/.htpasswd_RobotikI"
            elif lecture == 'RobotikII':
                url = 'https://relab.imes.uni-hannover.de/RobotikII'
                pwdFileName = "passwdRobotikII.txt"
                htpwdFileName = "/etc/nginx/.htpasswd_RobotikII"
            else:
                raise AttributeError('lecture muss MechSys, RobotikI oder RobotikII sein.')



            if user.username == 'imesAdmin':
                ans = subprocess.call(["htpasswd.py","-b",htpwdFileName,'imesAdmin',password])
                ans = subprocess.call(["htpasswd.py","-b",htpwdFileName+ "_admin",'imesAdmin',password])
            else:
                if not user.username == 'imesUser':
                    with open(pwdFileName, "a") as pwdFile:
                        pwdFile.write(user.username + ': ' + password + '\n')
                ans = subprocess.call(["htpasswd.py","-b",htpwdFileName,user.username,password])

            # Aktuelles Datum holen
            Datum = datetime.date.today()
            message="""<html>
            <head></head>
            <body>
            <h3>Herzlich Willkommen beim Remote Laboratory!</h3>
            <p>Um auf die Seite <a href='"""+ url +"""'>"""+url + """</a> zugreifen zu können, müssen Sie sich mit ihrem StudIP-Namen</p>
            <p style="margin-left:50px"><strong>"""+user.username+"""</strong></p>
            <p>als Benutzer anmelden. Das zugehörige Passwort ist:</p>
            <p style="margin-left:50px"><strong>"""+password+"""</strong></p>
            <p>Dieses können Sie nicht ändern und es wird auch nicht gespeichert. Bewahren Sie also diese Mail sorgfältig auf.</p>
            <p>Viel Spaß und gutes Gelingen wünscht das ReLab-Team!</p>
            </body>
            </html>"""
            msg = MIMEText(message,'html')
            msg['Subject'] = 'Informationen zum ReLab'
            msg['From'] = str(Header('ReLab <relab@imes.uni-hannover.de>'))
            msg['To'] = user.email
            time.sleep(12) # Bei zu schnellem Senden der Emails bricht die Verbindung ab.
            smtpserver.sendmail(msg['From'], [msg['To']], msg.as_string())
            user.password = True
            session.commit()
            print(datetime.datetime.now().strftime("%H:%M:%S") + ": " + user.username + " (user_id: " + str(user.user_id) + ")" + ' hat sein Passwort erhalten.')
            i_mail = i_mail + 1
            print('Mail Nr. ' + str(i_mail) + ' in diesem Durchlauf.')
            first = False
            # Muster: https://stackoverflow.com/questions/64505/sending-mail-from-python-using-smtp
    smtpserver.quit()
    print('Senden der Passwörter abgeschlossen.')


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Senden der User an den Eingangsserver")
    parser.add_argument('--lecture', metavar='Name', required=True,
                        help="Name der Vorlesung {MechSys, RobotikI, RobotikII}")
    args= parser.parse_args()
    main(lecture=args.lecture)
