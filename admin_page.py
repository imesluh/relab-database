from sqlalchemy import (
    create_engine,
    MetaData
)

import os

from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

import user_classes
from flask import Flask, url_for
from flask_admin import Admin
from flask_admin.contrib import sqla

from multiprocessing import Process

import sys
sys.path.insert(0, '/var/www/server/app')
import get_passwords as get_pw


import jinja2
from contextlib import contextmanager

@contextmanager
def session_scope(db_engine):
    """Provide a transactional scope around a series of operations."""
    session = Session(bind = db_engine, autocommit=False, autoflush=False)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        db_engine.dispose()

basedir = os.path.abspath(os.path.dirname(__file__))
pw_sql = get_pw.password_sql()
ip_server = get_pw.get_ip('SERVER_IP')
engine_mechsys = create_engine("mysql+pymysql://relab:" + pw_sql + "@" + ip_server + ":3306/MechSys")
metadata = MetaData(engine_mechsys)
Base = declarative_base()
User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
Base.metadata.create_all(engine_mechsys)

#Session = sessionmaker()
#Session.configure(bind=engine_mechsys)
#session_mechsys = Session(bind=engine_mechsys, autocommit=True)

engine_robotikI = create_engine("mysql+pymysql://relab:" + pw_sql + "@" + ip_server + ":3306/RobotikI")
metadata = MetaData(engine_robotikI)
Base = declarative_base()
User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
Base.metadata.create_all(engine_robotikI)

#Session = sessionmaker()
#Session.configure(bind=engine_robotikI)
#session_robotikI = Session(bind=engine_robotikI, autocommit=True)

engine_robotikII = create_engine("mysql+pymysql://relab:" + pw_sql + "@" + ip_server + ":3306/RobotikII")
metadata = MetaData(engine_robotikII)
Base = declarative_base()
User, Group, Reservation, Lab, Milestone, Solution = user_classes.initialize(Base)
Base.metadata.create_all(engine_robotikII)

#session_robotikII = Session(bind=engine_robotikII, autocommit=True)

app_mechsys = Flask(__name__)
app_mechsys.config['SECRET_KEY'] = 'nph6p86znph6puhw'
app_robotikI = Flask(__name__)
app_robotikI.config['SECRET_KEY'] = 'hm6793j9mn7wm5'
app_robotikII = Flask(__name__)
app_robotikII.config['SECRET_KEY'] = 'zn5wzk59mhizn'

class GroupAdmin(sqla.ModelView):
    def is_accessible(self):
        return True
    column_hide_backrefs = False
    column_list = ('name','group_id','user','score','reservation','labs')
    column_sortable_list =('name','score','reservation')
    column_searchable_list = ('name','group_id')
    def _group_formatter(view, context, model, name):
        return jinja2.Markup(
            u"<a href='%s'>%s</a>" % (
                url_for('group.index_view', search = '=' + str(model.group_id)),
                model.name)
        ) if model else u""

    def _reservation_formatter(view, context, model, name):
        return jinja2.Markup(
            u"<a href='%s'>%s</a>" % (
                url_for('reservation.index_view', search = '=' + str(model.group_id)),
                model.reservation)
        ) if model else u""

    def _user_formatter(view, context, model, name):
        first = True
        for user in model.user:
            if first:
                url = '<a href=' + url_for('user.index_view', search = '='+str(user.user_id)) + '>' + str(user) + '</a>'
                first=False
            else:
                url=url + ', <a href=' + url_for('user.index_view', search = '='+str(user.user_id)) + '>' + str(user) + '</a>'

        return jinja2.Markup(
            url
        ) if model else u""

    def _labs_formatter(view, context, model, name):
        return jinja2.Markup(
            u"<a href='%s'>%s</a>" % (
                url_for('lab.index_view', search = '=' + str(model.group_id)),
                'Labore')
        ) if model else u""

    column_formatters = {
        'name': _group_formatter,
        'reservation': _reservation_formatter,
        'user': _user_formatter,
        'labs': _labs_formatter
    }

class UserAdmin(sqla.ModelView):
    column_sortable_list =(('group','group.name'),'username','last_name','first_name')
    column_searchable_list = ('user_id','last_name','first_name','username')
    def _user_formatter(view, context, model, name):
        return jinja2.Markup(
            u"<a href='%s'>%s</a>" % (
                url_for('group.index_view', search = '=' + str(model.group.group_id)),
                model.group.name)
        ) if model.group else u""

    column_formatters = {
        'group': _user_formatter
    }

class ReservationAdmin(sqla.ModelView):
    column_sortable_list =('reservation','reservation_end','group')
    column_searchable_list = ('group_id',)
    def _group_formatter(view, context, model, name):
        return jinja2.Markup(
            u"<a href='%s'>%s</a>" % (
                url_for('group.index_view', search = '=' + str(model.group.group_id)),
                model.group.name)
        ) if model.group else u""

    def _lab_formatter(view, context, model, name):
        return jinja2.Markup(
            u"<a href='%s'>%s</a>" % (
                url_for('lab.index_view', search = '=' + str(model.group.group_id)),
                model.lab)
        ) if model.lab else u""

    column_formatters = {
        'group': _group_formatter,
        'lab' : _lab_formatter
    }

class LabAdmin(sqla.ModelView):
    column_hide_backrefs = False
    column_list = ('number','group_id','score','milestones','solutions','reservation','trys_allowed','trys_done','solutions_allowed','solutions_done')
    column_sortable_list= ('number','score','reservation','trys_done','solutions_done')
    column_searchable_list = ('group_id',)
    def _reservation_formatter(view, context, model, name):
        return jinja2.Markup(
            u"<a href='%s'>%s</a>" % (
                url_for('reservation.index_view', search = '=' + str(model.group_id)),
                model.reservation)
        ) if model.reservation else u""

    def _group_formatter(view, context, model, name):
        return jinja2.Markup(
            u"<a href='%s'>%s</a>" % (
                url_for('group.index_view', search = '=' +  str(model.group_id)),
                str(model.group_id))
        ) if model.group_id else u""

    def _milestone_formatter(view, context, model, name):
        first = True
        for milestone in model.milestones:
            if first:
                url = '<a href=' + url_for('milestone.edit_view', id = milestone.id, url=url_for('lab.index_view')) + '>' + ('1' if milestone.success else '0') + '</a>'
                first=False
            else:
                url=url + '<a href=' + url_for('milestone.edit_view', id= milestone.id,url=url_for('lab.index_view')) + '>' + (', 1' if milestone.success else ', 0') + '</a>'

        return jinja2.Markup(
            url
        ) if model.group else u""

    def _solution_formatter(view, context, model, name):
        return jinja2.Markup(
            u"<a href='%s'>%s</a>" % (
                url_for('solution.index_view', search = '=' +  str(model.id)),
                str(model.solutions))
        ) if model.solutions else u""

    column_formatters = {
        'group_id': _group_formatter,
        'milestones': _milestone_formatter,
        'reservation': _reservation_formatter,
        'solutions': _solution_formatter
    }

class MilestoneAdmin(sqla.ModelView):
    column_hide_backrefs = False
    column_list = ('id','number','success')
    column_searchable_list = ('id',)

class SolutionAdmin(sqla.ModelView):
    column_hide_backrefs = False
    column_list = ('success','values','score')
    column_searchable_list = ('lab_id',)

def start_admin_mechsys():
    with session_scope(engine_mechsys) as session:
        admin_mechsys = Admin(app_mechsys, name='MechSys', template_mode='bootstrap3',url='/MechSys/rest/admin')
        admin_mechsys.add_view(UserAdmin(User, session))
        admin_mechsys.add_view(GroupAdmin(Group, session))
        admin_mechsys.add_view(ReservationAdmin(Reservation, session))
        admin_mechsys.add_view(LabAdmin(Lab, session))
        admin_mechsys.add_view(MilestoneAdmin(Milestone, session))
        admin_mechsys.add_view(SolutionAdmin(Solution, session))
        app_mechsys.run('127.0.0.1',9090)

def start_admin_robotikI():
    with session_scope(engine_robotikI) as session:
        admin_robotikI= Admin(app_robotikI, name='RobotikI', template_mode='bootstrap3',url='/RobotikI/rest/admin')
        admin_robotikI.add_view(UserAdmin(User, session))
        admin_robotikI.add_view(GroupAdmin(Group, session))
        admin_robotikI.add_view(ReservationAdmin(Reservation, session))
        admin_robotikI.add_view(LabAdmin(Lab, session))
        admin_robotikI.add_view(MilestoneAdmin(Milestone, session))
        admin_robotikI.add_view(SolutionAdmin(Solution, session))
        app_robotikI.run('127.0.0.1',9091)

def start_admin_robotikII():
    with session_scope(engine_robotikII) as session:
        admin_robotikII= Admin(app_robotikII, name='RobotikII', template_mode='bootstrap3',url='/RobotikII/rest/admin')
        admin_robotikII.add_view(UserAdmin(User, session))
        admin_robotikII.add_view(GroupAdmin(Group, session))
        admin_robotikII.add_view(ReservationAdmin(Reservation, session))
        admin_robotikII.add_view(LabAdmin(Lab, session))
        admin_robotikII.add_view(MilestoneAdmin(Milestone, session))
        admin_robotikII.add_view(SolutionAdmin(Solution, session))
        app_robotikII.run('127.0.0.1',9092)

p1 = Process(target=start_admin_mechsys)
p1.start()
p2 = Process(target=start_admin_robotikI)
p2.start()
p3 = Process(target=start_admin_robotikII)
p3.start()

p1.join()
p2.join()
p3.join()
