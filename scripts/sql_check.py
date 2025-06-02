import sqlite3

conn = sqlite3.connect('gohealth.db')
cursor = conn.cursor()

print('Sample Patient Data')
for row in cursor.execute("SELECT * FROM patients LIMIT 2;"):
    print(row)

print('\nSample Visit Data')    
for row in cursor.execute("SELECT * FROM visits LIMIT 2;"):
    print(row)

print('\nSample Lab Data')   
for row in cursor.execute("SELECT * FROM lab_results LIMIT 2;"):
    print(row)

print('\nSample ICD Data')   
for row in cursor.execute("SELECT * FROM icd_reference LIMIT 2;"):
    print(row)

conn.close()
