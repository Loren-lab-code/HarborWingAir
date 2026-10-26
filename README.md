# HarborWing Air Database Project

## Project Overview
HarborWing Air is a relational database project developed for the IT8 activity. It demonstrates database design, relationships, SQL queries, and synthetic data generation.

## Project Structure
- `database/harborwing_schema.sql` — Creates the database tables.
- `database/example_queries.sql` — Contains example SQL queries.
- `database/row_counts.sql` — Verifies the number of records in each core table.
- `database/harborwing_air.mwb` — Editable MySQL Workbench model.
- `database/harborwing_air_eer.png` — Exported EER diagram.
- `data_generation/generate_data.py` — Generates fictional sample records.
- `data_generation/requirements.txt` — Lists the required Python packages.

## Technologies Used
- MySQL / MariaDB
- MySQL Workbench
- Python
- Faker
- mysql-connector-python

## Setup Instructions

1. Install and start your MySQL or MariaDB database server.
2. Create the `harborwing_air` database and execute `database/harborwing_schema.sql`.
3. Install the Python dependencies:

   `python -m pip install -r requirements.txt`

   Run this command from the `data_generation` folder, where `requirements.txt` is located.

4. Configure the database connection settings in `data_generation/generate_data.py`.
5. Back up any existing data, then generate the sample records:

   `python generate_data.py --reset`

   **Warning:** The reset option deletes existing records from the 11 core tables before repopulating them. Use only with your project database.

6. Execute `database/row_counts.sql` in MySQL Workbench to verify the records.
7. Execute `database/example_queries.sql` to test the example queries.
8. Open the `.mwb` file in MySQL Workbench to inspect the EER diagram.

## Database Documentation
The `database` folder contains the SQL scripts and exported diagram used to document the database structure and relationships.

## Sample Data
The project uses fictional demonstration data generated with Python Faker.

## Author
[Your Name]

## Course
IT8
