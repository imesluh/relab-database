from sqlalchemy import (
    ForeignKey,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    Boolean
    )
from sqlalchemy.orm import relationship

## Hier wird die Datenbank-Struktur festgelegt. Es gibt die Tabellen user, group,
## reservation, lab, milestone und solution. Diese haben verschiedene Beziehungen
## zueinander. Bspw. ist einer Reservierung genau ein Labor zugeordnet, einem Labor
## aber mehrere Milestones und einer Gruppe mehrere (i.d.R. 4) Labore.

def initialize(Base):
    class User(Base):
        __tablename__ = 'user'
        
        user_id = Column(Integer, primary_key=True)
        username = Column(String(30))
        last_name = Column(String(30))
        first_name = Column(String(30))
        group_id = Column(Integer, ForeignKey('group.group_id'))
        email = Column(String(100),nullable=False)
        password = Column(Boolean)
        
    
        group = relationship("Group", back_populates="user")

        def __repr__(self):
            return '%s %s' % (str(self.first_name),str(self.last_name))

    class Group(Base):
        __tablename__ = 'group'

        group_id = Column(Integer, primary_key=True)
        name = Column(String(30), unique=True)
        score = Column(Integer)

        user = relationship("User", back_populates="group")
        reservation = relationship("Reservation", back_populates="group")
        labs = relationship("Lab", backref='group',lazy='dynamic')
            

        def __repr__(self):
            return '%s - %s' % (str(self.name),str(self.group_id))


    class Reservation(Base):
        __tablename__ = 'reservation'
        id = Column(Integer, primary_key=True)
        group_id = Column(Integer, ForeignKey('group.group_id'))
        reservation = Column(DateTime,unique=True)#,nullable=False)
        reservation_end = Column(DateTime,unique=True)
        lab_id = Column(Integer, ForeignKey('lab.id'))
        lab = relationship("Lab", back_populates="reservation")

        group = relationship("Group", back_populates="reservation")

        def __repr__(self):
            return '%s - lab:%s' % (str(self.reservation),str(self.lab_id))


    class Lab(Base):
        __tablename__ = 'lab'
        id = Column(Integer, primary_key=True)
        group_id = Column(Integer, ForeignKey('group.group_id'))
        number = Column(Integer)
        score = Column(Integer)
        trys_allowed = Column(Integer)
        trys_done = Column(Integer)
        solutions_allowed = Column(Integer)
        solutions_done = Column(Integer)
        solutions = relationship("Solution", backref='lab')
        active_reservation = Column(Boolean)
        reservation = relationship("Reservation", back_populates="lab",uselist=False)
        milestones = relationship("Milestone", backref='lab',lazy='dynamic')
        def __repr__(self):
            return 'lab %s - id:%s' % (str(self.number),str(self.group_id))
        
    class Milestone(Base):
        __tablename__ = 'milestone'
        id = Column(Integer, primary_key=True)
        number = Column(Integer)
        success = Column(Boolean)
        lab_id = Column(Integer, ForeignKey('lab.id'))
        def __repr__(self):
            if self.success:
                return '1'
            else:
                return '0'

    class Solution(Base):
        __tablename__ = 'solution'
        id = Column(Integer, primary_key=True)
        lab_id = Column(Integer, ForeignKey('lab.id'))
        values = Column(Text)
        success = Column(Boolean)
        score = Column(Integer)
        def __repr__(self):
            if self.values == None:
                return ''
            if self.success:
                return 'Richtig: ' + str(self.score) + 'Pkt'
            else:
                return 'Falsch'

    return User, Group, Reservation, Lab, Milestone, Solution
