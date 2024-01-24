import streamsync as ss
from dotenv import load_dotenv
import psycopg2
import os
import json
import pandas as pd
# This is a placeholder to get you started or refresh your memory.
# Delete it or adapt it as necessary.
# Documentation is available at https://streamsync.cloud

load_dotenv(dotenv_path='../venv/.env')


PGHOST = os.getenv('PGHOST')
PGUSER = os.getenv('PGUSER')
PGPORT = os.getenv('PGPORT')
PGDATABASE = os.getenv('PGDATABASE')
PGPASSWORD = os.getenv('PGPASSWORD')
sql_query = """
SELECT 
    Name,
    SessionID,
    DateTimeOfChat,
    Severity AS "Urgency",
    Category AS "Team",
    Status AS "Chat Status"
FROM ChatRecords;
"""
summary_sql = """
SELECT ChatSummary FROM ChatRecords WHERE SessionID = '{}'
"""
transcript_sql = """
SELECT ChatTranscript FROM ChatRecords WHERE SessionID = '{}'
"""
severity_sql = """
SELECT Severity FROM ChatRecords WHERE SessionID = '{}'
"""
team_sql = """
SELECT Category FROM ChatRecords WHERE SessionID = '{}'
"""
sessionid_sql = """
SELECT SessionID FROM ChatRecords
"""
update_sql= """
UPDATE ChatRecords
SET Category = '{}', Severity = '{}'
WHERE SessionID = '{}';
"""
# Shows in the log when the app starts
print("Hello world!")

    
# Initialise the state

# "_my_private_element" won't be serialised or sent to the frontend,
# because it starts with an underscore
def update(state):
    connection = _init_db()
    cursor = connection.cursor()
    cursor.execute(update_sql.format(state['urgency'], state['team'], state['SSID']))
    connection.commit()
    cursor.close()
    connection.close()
    state.add_notification("success", "Confirmed", "Successfully Updated.")
    state['df'] = get_pandas()


def _init_db():
    cnx = psycopg2.connect(user=PGUSER, password=PGPASSWORD, host=PGHOST, port=PGPORT, database=PGDATABASE)
    return cnx


def get_pandas():
    connection = _init_db()
    df = pd.read_sql_query(sql_query, connection)
    connection.close()
    return df

def get_session_id(state, payload):
    state['SSID'] = payload
    connection = _init_db()
    cursor = connection.cursor()
    cursor.execute(summary_sql.format(payload))
    result = cursor.fetchone()[0]
    state["Summary"] = result
    cursor.execute(transcript_sql.format(payload))
    result = cursor.fetchone()[0]
    state["Transcript"] = result
    cursor.execute(severity_sql.format(payload))
    result = cursor.fetchone()[0]
    state['urgency'] = result
    cursor.execute(team_sql.format(payload))
    result = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    state['team'] = result
    state["visible"] = True


def get_sessionid_dropdown():
    connection = _init_db()
    cursor = connection.cursor()
    cursor.execute(sessionid_sql)
    result = cursor.fetchall()
    session_ids_dict = {session_id[0]: session_id[0] for session_id in result}
    cursor.close()
    return  session_ids_dict

initial_state = ss.init_state({
    "my_app": {
        "title": "Cura Dashboard"
    },
    "_my_private_element": 1337,
    "message": None,
    "counter": 26,
    "df": get_pandas(),
    "Summary": "",
    "Transcript": "",
    "SSID":'',
    "dict": get_sessionid_dropdown()
})