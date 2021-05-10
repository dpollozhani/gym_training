from google.oauth2 import service_account
from google.cloud import firestore
import pandas as pd
from datetime import datetime
from typing import List

def zip_sort_cols(*cols):
    zipped = list(zip(*cols))
    zipped_sorted = sorted(zipped, key=lambda x: (x[0], x[1]), reverse=True)
    return zipped_sorted

class GymSessionsDB:

    exercises = ['Squat', 'Deadlift', 'Bench press', 'Overhead press']

    def __init__(self, key_dict, project):
        self.__credentials = service_account.Credentials.from_service_account_info(key_dict)
        self.db = firestore.Client(credentials=self.__credentials, project=project)
        self.gym_sessions = self.db.collection('gym_sessions')
        self.gym_users = self.db.collection('gym_users')

    def create_document(self, document_data: dict) -> bool:
        doc = self.gym_sessions.document(document_id=str(datetime.now()))
        doc.create(document_data)
        if doc.get().to_dict() == document_data:
            return True
        return False

    def log_exercise(self, user:str, exercise: str, date: str, set_reps: List[int], set_weights: List[int]) -> bool:
        assert exercise in GymSessionsDB.exercises, f'exercise must be one of {GymSessionsDB.exercises}!'
        
        document_data = {'user': user,
                    'exercise': exercise,
                    'date': str(date),
                    'set_reps': set_reps,
                    'set_weights': set_weights
            }
        
        return self.create_document(document_data)
    
    def get_sessions(self) -> List[tuple]:
        documents = [(doc.id, doc.to_dict()) for doc in self.gym_sessions.stream() if doc.id.lower() != 'example']
        return documents

    def get_users(self) -> list:
        documents = [doc.to_dict()['alias'] for doc in self.gym_users.stream()]
        return documents

    def parse_dates(self, df) -> pd.DataFrame:
        df['created'] = df['created'].apply(lambda d: pd.to_datetime(d))
        df['date'] = df['date'].apply(lambda d: pd.to_datetime(d))
        return df

    def weight_reps(self, df) -> pd.DataFrame:
        return df.apply(lambda x: zip_sort_cols(x.set_weights, x.set_reps), axis=1)

    def add_best_set(self, df) -> pd.DataFrame:
        df['temp'] = self.weight_reps(df)
        df['best_set_weight'] = df['temp'].apply(lambda x: x[0][0])
        df['best_set_reps'] = df['temp'].apply(lambda x: x[0][1])
        df.drop(columns=['temp'], inplace=True)
        return df
    
    def add_total_weight(self, df) -> pd.DataFrame:
        df['temp'] = self.weight_reps(df)
        df['total_weight_lifted'] = df['temp'].apply(lambda x: sum([e[0]*e[1] for e in x]))
        df.drop(columns=['temp'], inplace=True)
        return df

    def fix_column_order(self, df) -> pd.DataFrame:
        return df[['user', 'date', 'exercise', 'set_weights', 'set_reps', 'best_set_weight', 'best_set_reps', 'total_weight_lifted', 'created']]
        
    def get_exercise_log(self) -> pd.DataFrame:
        documents = self.get_sessions()
        ids, records = [t[0] for t in documents], [t[1] for t in documents]
        
        df = pd.DataFrame.from_records(records)
        df['created'] = ids
        df = self.parse_dates(df)
        df = self.add_best_set(df)
        df = self.add_total_weight(df)
        df = self.fix_column_order(df)
        df = df.sort_values(by='created', ascending=False).reset_index(drop=True)
        return df        

    def validate_user(self, user: str) -> bool:
        documents = self.get_users()
        return user in documents

    def __repr__(self):
        return f'GymSessionsDB(db={self.db.project}, collections=[{self.gym_sessions.id},{self.gym_users}])'
