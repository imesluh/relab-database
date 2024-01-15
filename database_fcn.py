from sqlalchemy import (
    create_engine,
    MetaData,
    exc
    )
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import datetime
basedir = os.path.abspath(os.path.dirname(__file__))
from . import user_classes
import json


class Event:
    def __init__(self, ID, Title, Start, End, Edit, Color):
        self.ID = ID
        self.Title = Title
        self.Start = Start
        self.End = End
        self.Edit = Edit
        self.Color = Color

        
class connection:
    def __init__(self, url):
        self.url = url
        self.engine = create_engine(url)
        metadata = MetaData(self.engine)
        Base = declarative_base()
        self.User, self.Group, self.Reservation, self.Lab, self.Milestone, self.Solution = user_classes.initialize(Base)
        Base.metadata.create_all(self.engine)
        self.imes_user = ['imesUser','imesAdmin','imes-hiwi','imes-dozent']

    def is_imes_user(self, username):
        if username in self.imes_user:
            b_imes_user = True
        else:
            b_imes_user = False
        return b_imes_user

    def startsession(self):
        return Session(bind=self.engine, expire_on_commit=True)

    def reconnect(self):
        self.engine = create_engine(self.url)
        metadata = MetaData(self.engine)
        Base = declarative_base()
        self.User, self.Group, self.Reservation, self.Lab, self.Milestone, self.Solution = user_classes.initialize(Base)
        Base.metadata.create_all(self.engine)

    def check_connection(self):
        session = self.startsession()
        try:
            user = session.query(self.User).filter_by(username=self.imes_user[0]).first()
            session.close()
        except:
            session.close()
            self.reconnect()
        

    def get_score(self, user):
        """ Die Funktion gibt die Punkte fürs Ranking zurück. Own-Score als Tupel von (Punkte, Gruppenname) und scores als
            Liste von Tupels mit allen Gruppen (auch der eigenen). Auf diese Weise wird die eigene Gruppe farblich hervorgehoben.
        """
        self.check_connection()
        session = self.startsession()
        user = session.query(self.User).filter_by(username=user).first()
        scores = []
        own_score=[None, None]
        for group in session.query(self.Group):
            if (group.name is not None) and (group.score != None):
                if not group.name in self.imes_user:
                    if group == user.group:
                        own_score = [user.group.score, user.group.name]
                        scores.append(own_score)
                    else:
                        scores.append([group.score, group.name])
        session.close()
        return own_score, scores

    def get_reservations(self, user):
        """ Die Funktion gibt die aktuelle Reservierung von einem Nutzer (und damit der dazugehörigen Gruppe) zurück.
        """
        self.check_connection()
        session = self.startsession()
        curr_user = session.query(self.User).filter_by(username=user).first()
        reservation = curr_user.group.reservation
        session.close()
        return reservation

    def get_group(self, user):
        """ Die Funktion gibt die Gruppennummer eines Nutzers zurück.
        """
        self.check_connection()
        session = self.startsession()
        curr_user = session.query(self.User).filter_by(username=user).first()
        grp = curr_user.group.group_id
        session.close()
        return grp

    def get_labs(self, user):
        """ Die Funktion gibt die Labore eines Nutzers (und damit seiner Gruppe) zurück.
        """
        self.check_connection()
        session = self.startsession()
        curr_user = session.query(self.User).filter_by(username=user).first()
        labs = curr_user.group.labs.all()
        session.close()
        return labs

    def get_lab(self, user, reserv):
        """ Die Funktion gibt die Labornummer eines Nutzers (und damit seiner Gruppe) für eine bestimmte Reservierung zurück.
        """
        self.check_connection()
        session = self.startsession()
        user = session.query(self.User).filter_by(username=user).first()
        grp = user.group
        lab = -1
        #if str(user) == 'admin imes':
            #lab = 2
            #session.close()
            #return lab
        for reservation in user.group.reservation:
            if reservation.reservation == reserv:
                lab = reservation.lab.number
        session.close()
        return lab

    def groupname(self, user, name):
        """ Die Funktion setzt den Gruppennamen für die Gruppe, zu der user gehört.
        """
        self.check_connection()
        session = self.startsession()
        user = session.query(self.User).filter_by(username=user).first()
        grp = user.group
        grp.name = name
        try:
            session.commit()
            return True
        except exc.IntegrityError:
            session.rollback()
            session.close()
            return False

    
    def create(self, user, reserv, lab):
        """ Dei Funktion erzeugt eine Buchung für die Gruppe, zu der der user gehört, die Start- und Endzeit in reserv sowie das Labor lab.
        """
        self.check_connection()
        session = self.startsession()
        if user == self.imes_user[1]:
            # TODO: Abfrage wird so nie erfuellt
            user = session.query(self.User).filter_by(username=user).first()
            grp = user.group
            add_reservation=self.Reservation(group_id=grp.group_id,reservation=reserv[0],reservation_end=reserv[1], lab = grp.labs.filter_by(number=lab-1).first())
            session.add(add_reservation)
            session.commit()
            return True
        else:
            user = session.query(self.User).filter_by(username=user).first()
            grp = user.group
            # --- Wartung
            #if (lab == 2) and not ((str(grp.name) == 'testUser') or (user.group.name == self.imes_user[0])):
            #    session.close()
            #    return 0,'Der Versuch 2 wird zurzeit gewartet, bitte versuche es später erneut!',False
            # --- Wartung
            grps = session.query(self.Group)
            for group in grps:
                if group.group_id==1000:
                    for res in group.reservation:
                        if res.reservation is not None:
                            if (res.reservation-reserv).total_seconds()<1800  and (res.reservation_end-reserv).total_seconds()>0:
                                session.close()
                                return 0,'Der gewünschte Termin ist durch den Admin blockiert..',False 
                else:
                    if reserv == (group.reservation[0].reservation):
                        session.close()
                        return 0,'Der gewünschte Termin ist von einer anderen Gruppe gebucht.',False
            grp.reservation[0].reservation = reserv
            grp.reservation[0].lab = grp.labs.filter_by(number=lab-1).first()
            grp.reservation[0].lab.active_reservation = True
            trys_remain = grp.reservation[0].lab.trys_allowed-grp.reservation[0].lab.trys_done
            session.commit()
            return trys_remain, '',True
    

    def initialize(self,user,color_own,color_foreign):
        """ Die Funktion gibt die Resrevierungen für den Kalender zurück (verschiedene Farben für eigene und fremde Resrvierungen in einer eventlist) und, ob ein Gruppenname vorhanden ist.
        """
        self.check_connection()
        session = self.startsession()
        user = session.query(self.User).filter_by(username=user).first()
        group = int(user.group.group_id)
        newname=False
        if user.group.name is None: # Muss die Gruppe noch einen Namen wählen?
            newname = True
        reservations = session.query(self.Reservation).all()
        eventlist = []
        for reservation in reservations:
            if reservation.reservation is not None:
                if reservation.group_id == 1000:
                    if group==1000:
                        eventlist.append(json.dumps({'ID': group, 'Name': 'Event', 'Title': 'admin', 'Start': datetime.datetime.isoformat(reservation.reservation), 'End': datetime.datetime.isoformat(reservation.reservation_end), 'Edit': True, 'Color': color_own}))
                    else:
                        eventlist.append(json.dumps({'ID': 1000, 'Name': 'Event', 'Title': 'admin', 'Start': datetime.datetime.isoformat(reservation.reservation), 'End': datetime.datetime.isoformat(reservation.reservation_end), 'Edit': False, 'Color': color_foreign}))
                elif reservation.group_id == group:
                    eventlist.append(json.dumps({'ID': group, 'Name': 'Event', 'Title': 'Labor ' + str(reservation.lab.number + 1), 'Start': datetime.datetime.isoformat(reservation.reservation), 'End': datetime.datetime.isoformat(reservation.reservation +datetime.timedelta(0,30*60)), 'Edit': True, 'Color': color_own}))
                else:
                    eventlist.append(json.dumps({'ID': reservation.group_id, 'Name': 'Event', 'Title': 'Geblockt', 'Start':  datetime.datetime.isoformat(reservation.reservation), 'End': datetime.datetime.isoformat(reservation.reservation +datetime.timedelta(0,30*60)), 'Edit': False, 'Color': color_foreign}))
        session.close()
        return eventlist, group, newname

    def delete(self, user):
        """ Die Funktion löscht die Reservierung des Nutzers (und damit seiner Gruppe). Achtung! Dies funktioniert nicht für Admins, da dort mehrere Resrvierungen vorhanden sein können.
        """
        self.check_connection()
        session = self.startsession()
        user = session.query(self.User).filter_by(username=user).first()
        grp = user.group
        if (-30*60<(grp.reservation[0].reservation-datetime.datetime.now()).total_seconds()<60) and not (grp.name in self.imes_user) and not (str(grp.name) == 'testUser'):
            session.close()
            return False, 'Die Reservierung konnte nicht gelöscht werde, da sie schon begonnen hat oder bald beginnt.' 
        if grp.reservation[0].reservation is not None:
            grp.reservation[0].reservation = None
        session.commit()
        return True, ''


    def change(self, reserv, user):
        """ Die Reservierung eines Nutzers (und damit seiner Gruppe) wird auf eine andere Zeit verschoben
        """
        self.check_connection()
        session = self.startsession()
        user = session.query(self.User).filter_by(username=user).first()
        grp = user.group
        if grp.reservation[0].lab.trys_done >= grp.reservation[0].lab.trys_allowed:
            session.close()
            return False, 'Sie habe die maximale Anzahl an Versuchen absolviert.', ''
        grps = session.query(self.Group)
        for group in grps:
            if group.group_id==1000:
                for res in group.reservation:
                    if res.reservation is not None:
                        if (res.reservation-reserv).total_seconds()<1800  and (res.reservation_end-reserv).total_seconds()>0:
                            session.close()
                            return False,'Der gewünschte Termin ist durch den Admin blockiert.',''
            else:
                if reserv == (group.reservation[0].reservation):
                    session.close()
                    return False,'Der gewünschte Termin ist bereits von einer anderen Gruppe reserviert.',''
        grp.reservation[0].reservation = reserv
        trys_remain = grp.reservation[0].lab.trys_allowed-grp.reservation[0].lab.trys_done
        session.commit()
        return True, '',trys_remain

    def write_milestone(self, user, lab_number, milestone_number):
        """
        Die Funktion setzt einen Meilenstein (Index) eines Labors für den Nutzer (und seiner Gruppe).

        :param lab_number: number of current lab, indexing starts with 0!
        :type lab_number: int
        :param milestone: index of milestone to be written, indexing starts with 0
        :type milestone: int
        """
        self.check_connection()
        session = self.startsession()
        user = session.query(self.User).filter_by(username=user).first()
        grp = user.group
        print("db.write_milestone()")
        grp.labs.filter_by(number=lab_number).first().milestones[milestone_number].success = True
        session.commit()
        return True

    def get_milestones(self, user, lab_number):
        """ Die Funktion gibt den Milestones-Vektor (True oder False für jedem Milestone) für einen Nutzer und ein Labor zurück.
        """
        self.check_connection()
        session = self.startsession()
        user = session.query(self.User).filter_by(username=user).first()
        grp = user.group
        milestones = grp.labs.filter_by(number=lab_number).first().milestones
        ms_vector = []
        for ms in milestones:
            ms_vector.append(ms.success)
        session.close()
        return ms_vector

    def get_group_solution(self, user, labnumber):
        """ Die Funktion ermittelt, ob noch Lösungen durch eine Gruppe (und den Nutzer) übermittelt werden dürfen.
        """
        self.check_connection()
        session = self.startsession()
        user = session.query(self.User).filter_by(username=user).first()
        group = user.group
        if group.labs[labnumber].solutions_allowed > group.labs[labnumber].solutions_done:
            reason=''
            allowed = True
            trys = group.labs[labnumber].solutions_allowed-group.labs[labnumber].solutions_done-1
        else:
            allowed = False
            reason='Sie haben die maximale Anzahl an Lösungsversuchen erreicht'
            trys = group.labs[labnumber].solutions_allowed-group.labs[labnumber].solutions_done
        session.commit()
        return group.group_id, allowed, reason, trys

    def get_solution(self, user, labnumber):
        """ Die Funktion gibt die Werte der letzten übermittelten richtigen Lösung des Nutzers (und damit seiner Gruppe) zurück.
        """
        self.check_connection()
        session = self.startsession()
        user = session.query(self.User).filter_by(username=user).first()
        sol = False
        for solution in user.group.labs[labnumber].solutions:
            if solution.values is not None and solution.success:
                sol = solution.values
        session.close()
        return sol

    def write_solution(self, group, solution, labnumber):
        """ Die Funktion schreibt eine Lösung (als String) für eine Gruppe und ein bestimmtes Labor.
        """
        self.check_connection()
        session = self.startsession()
        group = session.query(self.Group).filter_by(group_id=group).first()
        index = group.labs[labnumber].solutions_done
        group.labs[labnumber].solutions_done=group.labs[labnumber].solutions_done+1
        group.labs[labnumber].solutions[index].values = solution
        session.commit()
        return True

    def write_score(self, group, lab, score):
        """ Die Funktion schreibt eine Puntkzahl für ein bestimmtes Labor einer Gruppe.
        """
        self.check_connection()
        session = self.startsession()
        group = session.query(self.Group).filter_by(group_id=group).first()
        score = int(score)
        if not group.name in self.imes_user:
            if group.labs[lab].score is None:   # noch kein score in diesem Lab vorhanden
                group.labs[lab].score = score
                if group.score is None:         # noch kein Gesamtscore vorhanden
                    group.score = score
                else:
                    group.score = group.score + score
            elif score > group.labs[lab].score:
                group.score = group.score + score - group.labs[lab].score
                group.labs[lab].score = score
            # Gesamtscore als Summe der einzelnen Lab-Scores berechnen
            print("--- database_fcn.write_score(): ")
            score_total = 0
            for i in range(group.labs.count()):
                try:
                    score_total = score_total + group.labs[i].score
                except:
                    pass # noch kein Score im entsprechenden Lab geschrieben
            print("Total score = " + str(score_total))
            group.score = score_total
        session.commit()
        return True

    def get_labScore(self, group, lab):
        """ Die Funktion gibt die Punktzahl einer Gruppe für ein bestimmtes Labor zurück
        """
        self.check_connection()
        session = self.startsession()
        group = session.query(self.Group).filter_by(group_id=group).first()
        if group.labs[lab].score is None:  # noch kein score in diesem Lab vorhanden
            score = 0
        else:
            score = group.labs[lab].score
        session.close()
        return score

    def write_success(self, group,lab):
        """ Die Funktion definiert die letzte übermittelte Lösung als korrekt.
        """
        self.check_connection()
        session = self.startsession()
        group = session.query(self.Group).filter_by(group_id=group).first()
        index = group.labs[lab].solutions_done-1
        group.labs[lab].solutions[index].success = True
        session.commit()
        return True

    def check_reservation(self, start, merker):
        """ Die Funktion schaut, ob eine Reservierung für einen Startzeitpunkt existiert. Der Merker dient der Überprüfung, ob
            eine Gruppe während des 30 Minuten-Blocks reserviert (just in time). Ist dem so, wird nach einmaligem Erhöhen der
            Versuchsanzahl der Merker auf den anderen Wert gesetzt, damit nur eine einamlige Erhöhung stattfindet.
        """
        self.check_connection()
        session = self.startsession()
        Reservations = session.query(self.Reservation).all()
        for reservation in Reservations:
            if reservation.reservation is not None and not reservation.group_id == 1000:
                if -1<abs((reservation.reservation-start).total_seconds())<1:
                    reservation.lab.trys_done= reservation.lab.trys_done+1
                    if merker ==1:
                        merker=2
                    else:
                        merker=1
        session.commit()
        return merker
