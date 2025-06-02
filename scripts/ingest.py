import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path('../data/raw')
OUTPUT_DIR = Path('../data/cleaned')
LOG_FILE = Path('../data/monitoring') / 'orphaned_insurance_ids_log.txt'
PLACEHOLDERS = {'', 'invalid', 'dob', 'n/a', 'na', 'none', 'unknown', '??'}

def normalize_date(date_str):
    if pd.isna(date_str) or not isinstance(date_str, str):
        return pd.NaT
    
    date_str = date_str.strip()
    if not date_str:
        return pd.NaT

    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",  
        "%Y/%m/%d",  
        "%m.%d.%Y",  
        "%m-%d-%Y",    
        "%Y.%m.%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return pd.NaT

def replace_placeholders(df: pd.DataFrame, placeholders: set) -> pd.DataFrame:
    return df.map(
        lambda x: pd.NA if isinstance(x, str) and x.strip().lower() in placeholders else x
    )

def clean_billable_amount(df):
    df['billable_amount'] = (
        pd.to_numeric(df['billable_amount'], errors='coerce')
        .fillna(0.0)
        .astype(float)
    )
    return df

def main():
    # Load data
    patients_df = pd.read_csv(DATA_DIR / 'patient_data.csv', dtype=str)
    visits_df = pd.read_csv(DATA_DIR / 'visit_data.csv', dtype=str)
    labs_df = pd.read_csv(DATA_DIR / 'lab_results.csv', dtype=str)
    icd_df = pd.read_csv(DATA_DIR / 'icd_reference.csv', dtype=str)

    # Replace placeholder strings with pd.NA (null)
    patients_df = replace_placeholders(patients_df, PLACEHOLDERS)
    visits_df = replace_placeholders(visits_df, PLACEHOLDERS)
    labs_df = replace_placeholders(labs_df, PLACEHOLDERS)
    icd_df = replace_placeholders(icd_df, PLACEHOLDERS)

    # Normalize dates
    patients_df['date_of_birth'] = patients_df['date_of_birth'].apply(normalize_date)
    patients_df['insurance_effective_date'] = patients_df['insurance_effective_date'].apply(normalize_date)
    visits_df['visit_date'] = visits_df['visit_date'].apply(normalize_date)
    visits_df['follow_up_date'] = visits_df['follow_up_date'].apply(normalize_date)
    labs_df['date_performed'] = labs_df['date_performed'].apply(normalize_date)
    labs_df['date_resulted'] = labs_df['date_resulted'].apply(normalize_date)
    icd_df['effective_date'] = icd_df['effective_date'].apply(normalize_date)
    
    
    # Normalize price numbers to float
    visits_df = clean_billable_amount(visits_df)

    # Data integrity checks
    assert patients_df['patient_id'].is_unique
    assert patients_df['patient_id'].notna().all()
    assert visits_df['visit_id'].is_unique
    assert visits_df['visit_id'].notna().all()
    assert visits_df['patient_id'].notna().all()
    assert labs_df['lab_id'].is_unique
    assert labs_df['lab_id'].notna().all()
    assert labs_df['visit_id'].notna().all()
    assert icd_df['status'].isin(["Active", "Inactive"]).all()

    # Find orphaned insurance IDs (insurance_id with no owner)
    orphaned = patients_df[
        patients_df['insurance_id'].notna() &
        patients_df['first_name'].isna() &
        patients_df['last_name'].isna()
    ]
    
    # Log orphaned insurance IDs
    with open(LOG_FILE, 'w') as f:
        if orphaned.empty:
            f.write("No orphaned insurance IDs found.\n")
        else:
            f.write(f"Orphaned insurance IDs found ({len(orphaned)} rows):\n")
            f.write(orphaned.to_string(index=False))
            f.write('\n')

    # Save cleaned data to CSV
    patients_df.to_csv(OUTPUT_DIR / 'patients_clean.csv', index=False, na_rep='null')
    visits_df.to_csv(OUTPUT_DIR / 'visits_clean.csv', index=False, na_rep='null')
    labs_df.to_csv(OUTPUT_DIR / 'labs_clean.csv', index=False, na_rep='null')
    icd_df.to_csv(OUTPUT_DIR / 'icd_clean.csv', index=False, na_rep='null')
    
    print("Ingestion / Cleaning Complete!")
    
if __name__ == "__main__":
    main()
