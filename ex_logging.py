import streamlit as st
from gym_sessions import GymSessionsDB
from ex_performance import _get_log

def _is_valid_user(db, user):
    return db.validate_user(user)

def _submit_log(db, user, exercise, date, set_reps, set_weights) -> bool:
    return db.log_exercise(user, exercise, date, set_reps, set_weights)

def app(db, default_user):
    #Submit username
    username = st.text_input('Username:', value=default_user, help=f'"{default_user}" per default. Submit your personal username; contact your guy if you have none.')
    
    if _is_valid_user(db, username):
        with st.sidebar:
            st.subheader('Logging settings')
            number_of_exercises = st.number_input('#of exercises', min_value=1, max_value=len(GymSessionsDB.exercises), value=1)
            number_of_sets = st.number_input('#of sets per exercise', min_value=1, max_value=5, value=3)

        st.markdown('## Log exercises')
        st.caption('Change settings in sidebar menu (you might have to tilt your mobile device).')
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
                        w = st.number_input(f'Weight', min_value=30.0, max_value=150.0, value=50.0, step=2.5, key=f'set_{j}_w')
                        set_reps.append(r)
                        set_weights.append(w)
                        st.write('-------')
                    submit = st.form_submit_button('Log')

                if submit:
                    _submit_log(db, username, exercise, date, set_reps, set_weights)
                    st.write('Success!')
                    log = _get_log(db)
                    last_log = log[log['user'] == username].iloc[0,:]
                    last_exercise, last_date, last_logged = last_log['exercise'], last_log['date'], last_log['created']
                    last_date_formatted = str(last_date).split(' ')[0]
                    st.write(f'Your last logged exercise: *{last_exercise}*, **{last_date_formatted}** (logged at **{last_logged}**.')
                    
    else:           
        st.error('Username is not recognized. If you want to get in, just tell us, dude :wink:')
