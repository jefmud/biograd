import sys
from flask import (abort, flash, Flask, g, redirect,
                   render_template, request, send_from_directory, session, url_for)
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor

from tinymongo import TinyMongoClient, Query, where
import admin
from gcollections import (demographic_responses_pull, progress_responses_pull, students_from_demog, advisors_from_students, drop_collection)

app = Flask(__name__)
app.secret_key = 'ChangeMeToSomethingSecret'
connection = TinyMongoClient()
DB = connection.biograd
Bootstrap(app)
ckeditor = CKEditor(app)
admin.initialize(app, DB)

# view some raw dictionary from mongo doc as html and form at jinja template
from dict2html import dict2html, dict2form, dict2form_schema, modal_wrapper
# assign filters (pattern)
# app.jinja_env.filters['filtername'] = filterfunc
app.jinja_env.filters['dict2html'] = dict2html
app.jinja_env.filters['dict2form'] = dict2form
app.jinja_env.filters['dict2form_schema'] = dict2form_schema
app.jinja_env.filters['modal_wrapper'] = modal_wrapper

def cli_confirm(prompt):
    """a Y/N confirmation command line prompt"""
    if input(prompt + ' type "CONFIRM" ')=='CONFIRM':
        return True
    return False

def drop_named_collections(db, args):
    """drops ONE collection named in args list
    args is list (typically passed in from sys.argv
    required '--drop'
    list can have 'advisors', 'relationships', 'students'
    """
    idx = args.index('--drop')
    if idx > -1 and idx < len(args):
        for col in args[idx+1:]:
            if cli_confirm('DROP collection "{}"'.format(col)):
                if drop_collection(db, col):
                    print("DROPPED {} collection".format(col))
                else:
                    print("An error was encountered dropping collection")
    sys.exit(0)

def initialize(args):
    # should be "graftable" to initialize function of boilerplate
    pass
        
@app.before_request
def before_request():
    """should be consistent with boilerplate"""
    g.db = DB
    g.theme = 'united' # bootswatch theme name


@app.route('/')
def index():
    return render_template('student/student_menu.html')

@app.route('/progress/pull')
def progress_pull():
    """pull progress data from qualtrics and store in db"""
    progress_responses_pull()
    return "see console for results"


@app.route('/demographics/pull')
def demographics_pull():
    """pull demographic data from qualtrics and store in db"""
    demographic_responses_pull()
    return "see console for results"

@app.route('/students/update')
def students_update():
    students_from_demog()
    return "see console for results"

@app.route('/students')
def students_all():
    docs = g.db.students.find({})
    return render_template('student/students_all.html', docs=docs)

@app.route('/student/<sid>')
def student_view(sid):
    schema = [
        ('DEMOG_1_TEXT', 'Firstname'),
        ('DEMOG_2_TEXT', 'Lastname'),
        ('DEMOG_4_TEXT', 'Nickname'),
        ('DEMOG_3_TEXT', 'SID'),
        ('DEMOG_5_TEXT', 'WFU Email'),
        ('DEMOG_6_TEXT', 'Alternate Email')
    ]
    doc = g.db.students.find_one({'DEMOG_3_TEXT':sid})
    if doc:
        relations = g.db.relations.find({'student':doc['_id']})
        advisors = []
        for relation in relations:
            this_advisor = g.db.advisors.find_one({'_id':relation['advisor']})
            if this_advisor and this_advisor['email']:
                advisors.append(this_advisor)
                
        progress_reports = g.db.progress.find({'DEMOG_3_TEXT':doc['DEMOG_3_TEXT']})
        return render_template('student/student_view.html', doc=doc, schema=schema, advisors=advisors, progress_reports=progress_reports)
    else:
        flash("That student ID did not match any existing records", category="warning")
        return redirect(url_for("students_all"))
    
@app.route('/advisors/update')
def advisors_update():
    """update advisors from student records"""
    advisors_from_students()
    return redirect(url_for('advisors_all'))

@app.route('/advisors')
def advisors_all():
    """return a view of all advisors"""
    docs = g.db.advisors.find({})
    return render_template('student/generic_docs.html', docs=docs, title="All Advisors")

@app.route('/advisor/update/<id>', methods=['GET','POST'])
def advisor_update(id):
    """modify and advisor"""
    doc = g.db.advisors.find_one({'_id':id})
    if request.method == 'POST':
        form_data = request.form
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        affilliation = request.form.get('affil')
    schema = [('firstname','First Name','firstname'), ('lastname', 'Last Name','lastname'), ('email', 'Email'), ('affiliation', 'Affiliation')]
    return render_template('student/generic_doc_schema_form.html', doc=doc, schema=schema, title='Update Advisor')

@app.route('/advisor/<id>')
def advisor_view(id):
    """advisor view and relationships to students"""
    doc = g.db.advisors.find_one({'_id':id})
    return render_template('student/generic_doc.html', doc=doc, title="Advisor")

@app.route('/advisor_mod/<id>')
def advisor_mod_view(id):
    """advisor view and relationships to students"""
    doc = g.db.advisors.find_one({'_id':id})
    return render_template('student/generic_modal_doc.html', doc=doc, title="Advisor")

@app.route('/progress')
def progress_all():
    """dump all progress responses to screen"""
    docs = g.db.progress.find({})
    return render_template('student/generic_docs.html', docs=docs, title="All Progress Reports")

@app.route('/progress/<id>')
def progress_view(id):
    doc = g.db.progress.find_one({'_id':id})
    return render_template('student/generic_doc.html', doc=doc, title='Progress Report')


@app.route('/demographics')
def demographics_all():
    """dump all demographics to screen"""
    output = []
    docs = g.db.demog.find({})
    return render_template('student/generic_docs.html', docs=docs, title="All Demographic Records")

@app.route('/demographics/sid/<sid>')
def demographics_sid(sid):
    return "todo"

@app.route('/testdict',methods=['GET','POST'])
def testdict():
    doc = {'name':'record collection',
           'count': 3,
           'albums': ['Dark side of the Moon',
                      'Revolver', 'Sgt. Pepper\'s Lonely Hearts Club Band',
                    'Get out of the heat'],
           'person': {"firstname":'Nigel', "lastname":'Tuffnel', 'roles': 'lead guitar, vocals, writer'}
           }
    if request.method == 'POST':
        form_data = request.form
        return render_template('student/generic_doc.html', doc=form_data)
    schema = [('person','Personal Data'), ('separator','-'), ('albums','Albums that are great')]
    return render_template('student/generic_doc_schema_form.html', doc=doc, schema=schema, title='Structure Test')
    
    
if __name__ == '__main__':
    if '--initialize' in sys.argv:
        initialize(sys.argv)
    if '--drop' in sys.argv:
        drop_named_collections(DB, sys.argv)
    app.run()