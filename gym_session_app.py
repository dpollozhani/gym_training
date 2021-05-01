import json
import streamlit as st
from gym_sessions import GymSessionsDB
import os
from datetime import datetime

def _connect():
    key_dict = json.loads(st.secrets['textkey'])
    db = GymSessionsDB(key_dict=key_dict, project='panas-onic2001')
    return db

def _submit_log(db, user, exercise, date, set_reps, set_weights):
    return db.log_exercise(user, exercise, date, set_reps, set_weights)

def _get_log(db):
    return db.get_exercise_log()

@st.cache
def _get_min_max_date(log):
    min_datetime = datetime(log.date.min().year, log.date.min().month, log.date.min().day, 0, 0)
    max_datetime = datetime(log.date.max().year, log.date.max().month, log.date.max().day+1, 0, 0)
    return min_datetime, max_datetime

@st.cache
def _get_users(log):
    return list(set(log.user.values))

@st.cache
def _get_exercises(log):
    return list(set(log.exercise.values))

default_user = 'drilon'

#Inital sidebarview for "password"
sidebar = st.sidebar

with sidebar:
    subheader_placeholder = st.empty()
    excersises_placeholder = st.empty()
    sets_placeholder = st.empty()
    st.write('------')
    password = st.text_input('How much?', help='You take?')
    answer_placeholder = st.empty()

if password.lower() == 'only full weight':

    #Set up database connection
    db = _connect()

    #Header
    st.image('img/barbell_img.jpeg', use_column_width=True)
    st.title('Gym session logging and followup')
    st.subheader('Weightlifting with barbells')
    st.caption('dpollozhani | pana$-onic2001')

    username = st.text_input('Username:', value=default_user, help=f'"{default_user}" per default')

    #Sidebar
    with sidebar:
        subheader_placeholder.subheader('Logging config')
        number_of_exercises = excersises_placeholder.number_input('#of exercises', min_value=1, max_value=len(GymSessionsDB.exercises), value=1)
        number_of_sets = sets_placeholder.number_input('#of sets per exercise', min_value=1, max_value=5, value=3)
        answer_placeholder.write('Exactly :wink:')

    logging = st.beta_expander('Log exercises', expanded=True)
    followup = st.beta_expander('Past performance', expanded=False)

    #Logging exercises
    with logging:
        st.markdown('**Log excercises**')
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
                    _submit_log(db, username, exercise, date, set_reps, set_weights)

    #Past performance
    with followup:
        st.markdown('**Past performance**')
        
        log = _get_log(db)

        available_users = _get_users(log)
        user_multiselect = st.multiselect('Users', options=available_users, default=default_user)
        
        available_exercises = _get_exercises(log)
        exercise_multiselect = st.multiselect('Exercises', options=available_exercises, default=available_exercises)
        
        min_datetime, max_datetime = _get_min_max_date(log)
        date_range = st.slider(
            'Date range', 
            min_value=min_datetime,
            value=min_datetime,
            max_value=max_datetime, 
            format="YYYY/MM/DD"
        )
        log = log[(log['date'] >= date_range) & (log['user'].isin(user_multiselect)) & (log['exercise'].isin(exercise_multiselect))]
        log['date'] = log['date'].dt.date
        st.write(log)