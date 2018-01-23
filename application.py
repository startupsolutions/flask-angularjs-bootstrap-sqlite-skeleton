
# Simple Flask + SQLAlchemy + Flask-Restless skeleton application

__author__ = 'Salvatore Carotenuto of StartupSolutions'


from flask import Flask, render_template, request, Response, jsonify, url_for
from flask_cors import CORS

from db_handler import DBHandler


app = Flask(__name__)

# === Application settings =============================================================================================

SERVER_PORT = 5000
API_PREFIX = '/api/v1'


# === CORS setting =====================================================================================================

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# === database handling ================================================================================================

dbhandler = DBHandler(database_file='test.db')


# === Routes definition ================================================================================================

@app.route('/')
def home():
    # code to automatically send origin urls
    if not request.script_root:
        # print "########## not request.script_root:"
        # this assumes that the 'home' view function handles the path '/'
        request.origin = {}
        request.origin['baseUrl'] = url_for('home', _external=True)
        request.origin['apiBaseUrl'] = request.origin['baseUrl'] + API_PREFIX[1:]
        print request.origin
    return render_template('index.html')


"""
# custom REST API routes:

@app.route(API_PREFIX + 'reminders', methods=['GET', 'POST'])
def reminders():
    if request.method == 'POST':
        data = request.json
        print "[POST] reminders: ", data
        dbHandler.storeReminder(data)
        #
        return Response(None, status=201, mimetype='application/json')
    #
    allReminders = dbHandler.allReminders()
    #
    return jsonify(allReminders)
"""


# --- Routes END -------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    #
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)
