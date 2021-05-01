import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Tuple
from gym_sessions import GymSessionsDB

def _get_log(db: GymSessionsDB) -> pd.DataFrame:
    return db.get_exercise_log()

@st.cache
def _get_min_max_date(log: pd.DataFrame) -> Tuple[datetime]:
    min_datetime = datetime(log.date.min().year, log.date.min().month, log.date.min().day, 0, 0)
    max_datetime = datetime(log.date.max().year, log.date.max().month, log.date.max().day+1, 0, 0)
    return min_datetime, max_datetime

@st.cache
def _get_users(log: pd.DataFrame) -> list:
    return list(set(log.user.values))

@st.cache
def _get_exercises(log: pd.DataFrame) -> list:
    return list(set(log.exercise.values))

#Past performance
def app(db, default_user):
    st.markdown('## Performance')
    
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