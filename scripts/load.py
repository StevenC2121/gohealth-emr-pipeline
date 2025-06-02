import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('sqlite:///gohealth.db')

# Load cleaned CSVs
patients_df = pd.read_csv('../data/cleaned/patients_clean.csv')
visits_df = pd.read_csv('../data/cleaned/visits_clean.csv')
labs_df = pd.read_csv('../data/cleaned/labs_clean.csv')
icd_df = pd.read_csv('../data/cleaned/icd_clean.csv')

# Write to SQLite
patients_df.to_sql('patients', engine, if_exists='replace', index=False)
visits_df.to_sql('visits', engine, if_exists='replace', index=False)
labs_df.to_sql('lab_results', engine, if_exists='replace', index=False)
icd_df.to_sql('icd_reference', engine, if_exists='replace', index=False)

print("Database Created!")
