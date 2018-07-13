# mongo doesn't use the concept of models, but collections of documents
# collections:
# -- demog_responses - raw qualtrics demographic responses
# -- progress_responses - raw qualtrics progress responses
# -- students - basic student profile, derived from demographic responses, refined for view/modification
# -- advisors - basic advisor profile, derived from demographic responses, refined for view/modification
# -- evals - advisor evaluations, simple data structure (SID, AID, date, title, description)
# -- artifacts - student artifacts, simple structure (SID, date, title, classification, description, file)

from flask import g
from json_utils import get_demog_JSON, get_progress_JSON

def drop_collection(db, collection_name):
    """drop a collection from db"""
    this_collection = db[collection_name]
    tdoc = this_collection.find_one({})
    try:
        # in a later version of TinyMongo collection.drop() will be implemented, for now, this will suffice
        this_collection.delete_many({})
        return True
    except Exception as e:
        return False
        

def demographic_responses_pull():
    """pull demographic responses into mongodb"""
    data = get_demog_JSON()
    for item in data:
        for rid, rdata in data.items():
            # see if response rid exists
            r = g.db.demog.find_one({'rid':rid})
            if r is None:
                rdata['rid'] = rid
                r = g.db.demog.insert_one(rdata)
                print("inserted demog record {} for {}".format(rid, rdata.get('EmailAddress')))

def progress_responses_pull():
    """pull progress responses into mongodb"""
    data = get_progress_JSON()
    for item in data:
        for rid, rdata in data.items():
            # see if response rid exists
            r = g.db.progress.find_one({'rid':rid})
            if r is None:
                rdata['rid'] = rid
                try:
                    r = g.db.progress.insert_one(rdata)
                    print("inserted progress record {} for {}".format(rid, rdata.get('EmailAddress')))
                except Exception as e:
                    print(e)

def progress_all():
    """returns the JSON of all progress"""
    pass

def demographics_all():
    """returns the JSON of all demographic responses"""
    pass

def students_from_demog():
    docs = g.db.demog.find({})
    for doc in docs:
        # if doc matches existing student doc (match on email) then update existing
        # else create new student doc
        semail = doc.get('EmailAddress')
        sdoc = g.db.students.find_one({'EmailAddress': semail})
        if sdoc:
            print("update {}".format(semail))
            # have to use a careful method to update, only consider "newer" doc that currently held date.
        else:
            print("create {}".format(semail))
            g.db.students.insert_one(doc)
        
    
def advisors_from_students():
    """get all the advisors from student docs"""
    docs = g.db.students.find({})
    adv = set()
    for doc in docs:
        # CM1 (committee member 1), CM2, CM3, CM4, CM5, CMX
        for member in ['CM1', 'CM2', 'CM3', 'CM4', 'CM5', 'CMX']:
            # create an advisor document
            this_advisor = {
                          'firstname': doc.get(member + '_1_TEXT','').strip(),
                          'lastname': doc.get(member + '_2_TEXT','').strip(),
                          'email': doc.get(member + '_3_TEXT','').strip(),
                          'affiliation': doc.get(member + '_4_TEXT','').strip()
            }
            
            adoc = g.db.advisors.find_one({'email': this_advisor['email']})
            if adoc is None:
                # create a new advisor record and update the document id
                aid = g.db.advisors.insert_one(this_advisor).inserted_id
                adoc = this_advisor
                adoc['_id'] = aid
            
            # create a relationship record if necessary
            this_relation = {'student':doc['_id'], 'advisor':adoc['_id']}
            rdoc = g.db.relations.find_one(this_relation)
            if rdoc is None:
                g.db.relations.insert_one(this_relation)
    
    # return list of advisors, why not?
    return g.db.advisors.find({})
            
        
        
if __name__ == '__main__':
    demographic_responses_pull()