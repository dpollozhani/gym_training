import streamlit as st
from gym_sessions import GymSessionsDB
from multiapp import MultiApp
import ex_logging, ex_performance
import json

def _connect() -> GymSessionsDB:
    key_dict = json.loads(st.secrets['textkey'])
    db = GymSessionsDB(key_dict=key_dict, project='panas-onic2001')
    return db

#Set up database connection
db = _connect()
default_user = 'drilon'

app = MultiApp()
app.add_app("Logging", ex_logging.app, db=db, default_user=default_user)
app.add_app("Performance", ex_performance.app, db=db, default_user=default_user)

#Header
st.title('Gym session logging and performance followup')
st.subheader('*Weightlifting with barbells*')
st.caption('dpollozhani | pana$-onic2001')

app.run()


