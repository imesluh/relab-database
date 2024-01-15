from sqlalchemy import create_engine
import csv
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import user_classes

import sys
sys.path.insert(0, '/var/www/server/app')
import get_passwords as get_pw

# Beispielaufruf
# python3 fill_db.py --lecture MechSys --filepath /var/www/server/db_server/user_imes.csv --labs 5 -ms 10 -ms 10 -ms 10 -ms 10 -ms 1 --try 7 --solutions 7 --adminMail relab@imes.uni-hannover.de
# python3 fill_db.py --lecture RobotikI --filepath /var/www/server/db_server/students_rob1.csv --labs 5 -ms 10 -ms 10 -ms 10 -ms 10 -ms 1 --try 7 --solutions 7 --adminMail relab@imes.uni-hannover.de
# python3 fill_db.py --lecture RobotikII --filepath /var/www/server/db_server/user_imes.csv --labs 5 -ms 10 -ms 10 -ms 10 -ms 10 -ms 1 --try 7 --solutions 7 --adminMail relab@imes.uni-hannover.de


def main(lecture, filepath, labs, milestones, trys, solutions, adminMail):
    if len(milestones) != labs:
        print('Für jedes Labor muss eine Anzahl an Milestones definiert werden.')
        return False
    basedir = os.path.abspath(os.path.dirname(__file__))
    pw_sql = get_pw.password_sql()
    ip_server = get_pw.get_ip('SERVER_IP')
    engine = create_engine("mysql+pymysql://relab:" + pw_sql + "@" + ip_server + ":3306/" + lecture)  # Access the DB Engine
    Base = declarative_base()

    User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
    Base.metadata.create_all(engine)

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    users = session.query(User).all()
    bExistDefaultUsers = False # Wenn die Admin-Nutzer (mit Nachnamen imes) vorhanden sind, werden diese nicht neu erstellt
    for user in users:
        if user.last_name == 'imes':
            bExistDefaultUsers = True

    with open(filepath, 'r', newline='', encoding='cp1250') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        next(spamreader, None)
        for row in spamreader:
            if "keiner Funktion" in row[0]:
                break
            else:
                print(row[0])
                group = [int(s) for s in row[0].strip('"\'').split() if s.isdigit()][0]
                print('############ Neuer User ###########################')
                print('Username = ' + row[5].strip('"\''))
                print('Nachname = ' + row[3].strip('"\''))
                print('Vorname = ' + row[2].strip('"\''))
                print('Gruppe = ' + str(group))
                print('Email = ' + row[8].strip('"\''))
                #print(abc)
                add_user =User(username = row[5].strip('"\''), last_name=row[3].strip('"\''), first_name=row[2].strip('"\''), group_id=group, email=row[8].strip('"\''), password=False)
                add_group = Group(group_id=group)
                add_reservation = Reservation(group_id=group)
                isin = False
                for group_id in session.query(Group.group_id):
                    if group == group_id[0]:
                        isin = True
                        break
                if not isin:
                    num_lab = 0
                    for milestone in milestones:
                        i = 0
                        add_lab = Lab(number = num_lab,trys_allowed=trys, trys_done=0,solutions_allowed=solutions,solutions_done=0, active_reservation = False)
                        while i < milestone:
                            add_milestone = Milestone(number = i, success = False)
                            add_lab.milestones.append(add_milestone)
                            i = i+1
                        i = 0
                        while i < solutions:
                            add_solution = Solution(success = False)
                            add_lab.solutions.append(add_solution)
                            i = i+1
                        add_group.labs.append(add_lab)
                        num_lab = num_lab+1
                    session.add(add_group)
                    session.add(add_reservation)
                session.add(add_user)
        if not bExistDefaultUsers:
            trys_DefaultUsers = 99
            print('############ admin ###########################')
            group=1000
            add_user =User(username = 'imesAdmin', last_name='imes', first_name='admin', group_id=group, email=adminMail, password=False)
            add_group = Group(group_id=group, name='imesAdmin')
            add_reservation = Reservation(group_id=group)
            num_lab = 0
            for milestone in milestones:
                i = 0
                add_lab = Lab(number = num_lab,trys_allowed=trys_DefaultUsers, trys_done=0,solutions_allowed=trys_DefaultUsers,solutions_done=0, active_reservation = False)
                while i < milestone:
                    add_milestone = Milestone(number = i, success = False)
                    add_lab.milestones.append(add_milestone)
                    i = i+1
                i = 0
                while i < solutions:
                    add_solution = Solution(success = False)
                    add_lab.solutions.append(add_solution)
                    i = i+1
                add_group.labs.append(add_lab)
                num_lab = num_lab+1
            session.add(add_group)
            session.add(add_reservation)
            session.add(add_user)


            print('############ imes_user ###########################')
            group=2000
            add_user =User(username = 'imesUser', last_name='imes', first_name='user', group_id=group, email=adminMail, password=False)
            add_group = Group(group_id=group, name='imesUser')
            add_reservation = Reservation(group_id=group)
            num_lab = 0
            for milestone in milestones:
                i = 0
                add_lab = Lab(number = num_lab,trys_allowed=trys_DefaultUsers, trys_done=0,solutions_allowed=trys_DefaultUsers,solutions_done=0, active_reservation = False)
                while i < milestone:
                    add_milestone = Milestone(number = i, success = False)
                    add_lab.milestones.append(add_milestone)
                    i = i+1
                i = 0
                while i < solutions:
                    add_solution = Solution(success = False)
                    add_lab.solutions.append(add_solution)
                    i = i+1
                add_group.labs.append(add_lab)
                num_lab = num_lab+1
            session.add(add_group)
            session.add(add_reservation)
            session.add(add_user)

        session.commit()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Erstellen der Database")
    parser.add_argument('--lecture', metavar='N', required=True, help="Die Vorlesung (MechSys, RobotikI oder RobotikII).")
    parser.add_argument('--filepath', metavar='path', required=True, help="Der Pfad zur csv-Datei.")
    parser.add_argument('--labs', metavar='N', required=True, help="Anzahl der Labore", type=int)
    parser.add_argument('-ms', '--milestones', metavar='[labsxN]', action='append', required=True, help="Die Anzahl der Milestones für jedes Labor (als Vektor)", type=int)
    parser.add_argument('--trys', metavar='N', required=False, help="Anzahl der Laborbuchungen", default=5, type=int)
    parser.add_argument('--solutions', metavar='N', required=False, help="Anzahl der Lösungsübermittlungen", default=7, type=int)
    parser.add_argument('--adminMail', metavar='N', required=True, help="Die Mailadresse für admin- und imes_user-Zugangsdaten")
    #parser.add_argument('--rebuild', action='store_true', required=False, help="Alle Einträge der Datenbank werden entfernt und neu aufgefüllt.", default=False)
    args = parser.parse_args()
    main(lecture = args.lecture, filepath=args.filepath, labs=args.labs, milestones=args.milestones, trys=args.trys, solutions=args.solutions,
         adminMail=args.adminMail)
