import csv
import json

# Function to convert CSV data to JSON format
def convert_csv_to_json(csv_file):
    data = []
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if "(Deputed)" in row['Name']:
                continue
            qualifications = row['Qualification'].split(',')
            specializations = row['Specialization'].split(',')
            formatted_row = {
                "name": row['Name'],
                "designation": row['Designation'],
                "department": row['Department'],
                "qualification": qualifications,
                "specialization": specializations,
                "teaching_experience_in_years": int(row['teach_exp'].split()[0]) if row['teach_exp'] else 0
            }
            data.append(formatted_row)
    return data

# Define the input CSV file path
csv_file_path = 'AU_employee_data.csv'

# Convert CSV data to JSON format
json_data = convert_csv_to_json(csv_file_path)

# Write JSON data to a file
with open('../documents/CSE/text/faculty.json', 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

print("JSON file created successfully.")
