import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from typing import Tuple
import base64
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

def _get_table_download_link(log: pd.DataFrame):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = log.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="gym_performance_log.csv">Export data</a>'
    return href

#Past performance
def app(db, default_user):
    st.markdown('## Performance')
    full_log = _get_log(db)

    available_users = _get_users(full_log)
    available_exercises = _get_exercises(full_log)
    min_datetime, max_datetime = _get_min_max_date(full_log)
    
    with st.beta_container():
        #Chart filters
        selection_col1, selection_col2 = st.beta_columns((1,4))
        user_select = selection_col1.selectbox('User', options=available_users)
        exercise_multiselect = selection_col2.multiselect('Exercises', options=available_exercises, default=available_exercises)

        date_range = st.slider(
            'Date range', 
            min_value=min_datetime,
            value=min_datetime,
            max_value=max_datetime, 
            format="YYYY/MM/DD"
        )

        log = full_log[(full_log['date'] >= date_range) & (full_log['user'] == user_select) & (full_log['exercise'].isin(exercise_multiselect))]
        log['date'] = log['date'].dt.date

        #Chart
        chart = alt.Chart(log).mark_circle().encode(
            alt.X('date', scale=alt.Scale(clamp=False, zero=False)),
            alt.Y('best_set_weight', scale=alt.Scale(zero=False, padding=1)),
            color='exercise',
            size='best_set_reps',
            tooltip=['exercise', 'best_set_weight', 'best_set_reps', 'total_weight_lifted', 'date'],
            ).properties(height=500).interactive()
        
        st.altair_chart(chart, use_container_width=True)

    with st.beta_expander('Show all data'):
        st.write(full_log)
        st.markdown(_get_table_download_link(full_log), unsafe_allow_html=True)