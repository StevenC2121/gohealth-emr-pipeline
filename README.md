# GoHealth Urgent Care EMR Data Engineering Assessment

## Description
This project processes and loads electronic medical records (EMR) data for GoHealth Urgent Care. It includes data ingestion, validation, transformation, and loading into a clean, structured format suitable for analytics and reporting.

## Extract
- Reads raw `.csv` files including:
  - Patient data
  - Visit records
  - Lab results
  - Diagnosis codes (ICD)

## Transformations
- Normalized inconsistent date formats (`01/15/2024`, `2024-01-15`, etc.) into YYYY-MM-DD format
- Handled missing or placeholder values (`"N/A"`, `"unknown"`, `"??"`, etc.)
- Ensured numeric fields are correctly typed and formatted (`billable_amount` normalized to float values)
- Validated categorical fields such as visit status (must be `Active` or `Inactive`)
- Split incorrectly joined columns in the dataset ("Check-up,Z00" in one column -> split "Check-up", Z00)

## Load
- Output written to a clean `.csv` file for each dataset
- Ready for downstream ingestion into data warehouses or analytics pipelines
  - Loaded data into a basic SQL database in Python and did basic queries on each set as an example

## Best Practices
- HIPAA Protected Health information
  - Protected health data includes (names, phone numbers, addresses, and more)
  - The ingestion script includes commented-out lines to optionally drop PHI fields (`first_name`, `last_name`, `address`, `phone`, etc.)
  - In a production environment, these fields would either be excluded or encrypted.
- Orphaned insurance accounts (accounts with no owner)
    - Logged any instance of insurance accounts with no owner
    - In a production environment this is a red flag and would need to be handled immediately
- Used `.gitignore` to exclude environment files
- Code organized in reusable functions for clarity and testing
- Validation functions ensure data quality

## External Libraries
- **Pandas**: Most important library used for the data pipeline. I used it for data ingestion, cleaning (date normalization, placeholders, etc.), data validation, and exporting clean data. I picked Pandas because it made the entire ETL process easier in Python. 
- **SQLAlchemy**: Used to define the destination database and load the cleaned data. I used SQLAlchemy because it was the easiest way to create a database, load, and query my data while still in my Python project.
- **datetime**: Used to normalize and validate date strings from multiple inconsistent formats into a single standard format (YYYY-MM-DD). It helps ensure all date fields (e.g. visit_date, date_of_birth) are parsed correctly and can be compared or sorted.
- **pathlib**: Used for handling file paths in a clean way. Instead of hardcoding file paths as strings, pathlib ensures compatibility across environments and improves code readability.

## Additional Considerations / Proposed Next Steps
- Encrypting / Masking PHI information couldn't be done in the timeframe but would be the first thing I worked on next.
  - Includes minor tweaks like keeping only the year of dates that directly relate to an individual (birth date)
- Slowly Changing Dimensions (Future Consideration)
  - The `patients` table currently stores only the latest known patient demographic and insurance info.
  - In a production environment, this would ideally be modeled as a Type 2 SCD:
    - Each change (new address or insurance) would insert a new versioned row.
    - Fields like `effective_date` and `end_date` would track history.
  - Due to time, SCD has been noted but not implemented here.
- Consider further logging and exception handling for production readiness
- Potential to include unit tests for validation logic

## Proposed Data Model
Patients
- **patient_id (Primary Key)**
- first_name
- last_name
- date_of_birth
- gender
- address
- city
- state
- zip
- phone
- insurance_id
- insurance_effective_date

Visits
- **visit_id (Primary Key)**
- **patient_id (Foreign Key → patients.patient_id)**
- provider_id
- visit_date
- location
- reason_for_visit
- **icd_code (Foreign Key → icd_reference.icd_code)**
- visit_status
- billable_amount
- currency
- follow_up_date

ICD_reference
- **icd_code (Primary Key)**
- description
- effective_date
- status

Lab_Results
- **lab_id (Primart Key)**
- **visit_id (Foreign Key → visits.visit_id)**
- test_name
- test_value
- test_units
- reference_range
- date_performed
- date_resulted
