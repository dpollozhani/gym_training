import json
import streamlit as st
from gym_sessions import GymSessionsDB
import os
from datetime import datetime

def _connect():
    key_dict = json.loads(st.secrets['textkey'])
    db = GymSessionsDB(key_dict=key_dict, project='panas-onic2001')
    return db

def _submit_log(db, exercise, date, set_reps, set_weights):
    return db.log_exercise(exercise, date, set_reps, set_weights)

def _get_log(db):
    return db.get_exercise_log()

@st.cache
def _get_min_max_date(log):
    min_datetime = datetime(log.date.min().year, log.date.min().month, log.date.min().day, 0, 0)
    max_datetime = datetime(log.date.max().year, log.date.max().month, log.date.max().day+1, 0, 0)
    return min_datetime, max_datetime

db = _connect()

st.image('img/barbell_img.jpeg', use_column_width=True)
st.title('Gym session logging and followup')
st.subheader('Weightlifting with barbells')
st.caption('dpollozhani | pana$-onic2001')

with st.sidebar:
    st.subheader('Logging config')
    number_of_exercises = st.number_input('#of exercises', min_value=1, max_value=len(GymSessionsDB.exercises), value=1)
    number_of_sets = st.number_input('#of sets per exercise', min_value=1, max_value=5, value=3)

logging = st.beta_expander('Log exercises', expanded=True)
followup = st.beta_expander('Past performance', expanded=False)

with logging:

    cols = st.beta_columns(number_of_exercises)

    for i, col in enumerate(cols):
        with col:
            with st.form(key=f'exercise_log_{i}'):
                date = st.date_input('Date', help='Select the date of the exercise')
                exercise = st.selectbox('Exercise', options=GymSessionsDB.exercises)
                set_reps, set_weights = [], []
                st.write('-------')
                for j in range(number_of_sets):
                    st.write(f'Set {j+1}')
                    r = st.number_input(f'Reps', min_value=1, max_value=15, value=5, key=f'set_{j}_r')
                    w = st.slider(f'Weight', min_value=30.0, max_value=150.0, value=50.0, step=2.5, key=f'set_{j}_w')
                    set_reps.append(r)
                    set_weights.append(w)
                    st.write('-------')
                submit = st.form_submit_button('Log')

            if submit:
                _submit_log(db, exercise, date, set_reps, set_weights)

with followup:
    log = _get_log(db)
    min_datetime, max_datetime = _get_min_max_date(log)
    date_range = st.slider(
        'Date range', 
        min_value=min_datetime,
        value=min_datetime,
        max_value=max_datetime, 
        format="YYYY/MM/DD"
    )
    log = log[log.date >= date_range]
    st.write(log)