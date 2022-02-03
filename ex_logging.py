import streamlit as st
import pandas as pd
from gym_sessions import GymSessionsDB
from ex_performance import _get_log

def _submit_log(db, user, exercise, date, set_reps, set_weights, comment) -> bool:
    return db.log_exercise(user, exercise, date, set_reps, set_weights, comment)

def _get_latest_weights(log, exercise, user):
    log = log[(log['user']==user) & (log['exercise']==exercise)]
    if len(log) > 0: 
        log = log[['created','exercise','worst_set_weight']]
        latest_date = log.groupby('exercise')['created'].max().reset_index()
        latest_per_exercise = pd.merge(latest_date, log, on=['exercise','created'], how='inner')
        latest_weights = dict(zip(latest_per_exercise['exercise'].values, latest_per_exercise['worst_set_weight'].values))
    else:
        latest_weights = {exercise: 40.0}
    return latest_weights

def app(db, default_user):
    #Submit username
    username = st.selectbox('User', [' ']+db.get_users())
    
    _exercises = db.get_exercises()

    if username != ' ':
        with st.sidebar:
            st.subheader('Logging settings')
            number_of_exercises = st.number_input('#of exercises', min_value=1, max_value=len(_exercises), value=1)
            number_of_sets = st.number_input('#of sets per exercise', min_value=1, max_value=5, value=3)

        st.markdown('## Log exercises')
        st.caption('Change settings in sidebar menu (you might have to tilt your mobile device).')


        cols = st.beta_columns(number_of_exercises)
        for i, col in enumerate(cols):
            with col:
     
                exercise_type = st.selectbox('Exercise type', options=list(_exercises.keys()), key=f'exercise_type{i}')
                exercise = st.selectbox('Exercise', options=_exercises[exercise_type], key=f'exercise{i}')
                latest_weights = _get_latest_weights(_get_log(db), exercise, username)
                with st.form(key=f'exercise_log_{i}'):
                    date = st.date_input('Date', help='Select the date of the exercise')
                    set_reps, set_weights = [], []
                    for j in range(number_of_sets):
                        st.write(f'Set {j+1}')
                        r = st.number_input(f'Reps', min_value=1, max_value=15, value=5, key=f'set_{j}_r')
                        min_w, max_w, def_w = max(10.0,latest_weights[exercise]-50), latest_weights[exercise]+100, latest_weights[exercise]
                        w = st.number_input(f'Weight', min_value=min_w, max_value=max_w, value=def_w, step=2.5, key=f'set_{j}_w')
                        set_reps.append(r)
                        set_weights.append(w)
                        st.write('-------')
                    st.write('Comment')
                    comment = st.text_input('Input here')
                    submit = st.form_submit_button('Log')

                if submit:
                    _submit_log(db, username, exercise, date, set_reps, set_weights, comment)
                    st.write('Success!')
                    log = _get_log(db)
                    last_log = log[log['user'] == username].iloc[0,:]
                    last_exercise, last_date, last_logged = last_log['exercise'], last_log['date'], last_log['created']
                    last_date_formatted = str(last_date).split(' ')[0]
                    st.write(f'Your last logged exercise: *{last_exercise}*, **{last_date_formatted}** (logged at **{last_logged}**.')
                    
    else:
        st.error('Please select your username (&#8593;) before continuing logging you life\'s greatest achievements :wink:')
        