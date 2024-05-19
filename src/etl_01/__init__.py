import pandas as pd
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime

import logging

# Source Connection
source = create_engine('postgresql+psycopg2://root:root@localhost:5432/source')

# Source Connection
target = create_engine('postgresql+psycopg2://root:root@localhost:5433/target')

# Example function to create and populate a sample table
def create_table(connection: Engine):
    try:
        with connection.connect() as conn:
            create_query = text('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    email TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute(create_query)
            conn.commit()
            logging.info("Table 'users' created successfully.")

    except SQLAlchemyError as e:
        logging.error(e)

def insert_data(connection: Engine):
    with connection.connect() as conn:
        # Insert sample data
        insert_query = text(
        '''
            INSERT INTO users (name, age, email)
            VALUES
                ('Alice', 25, 'alice@example.com'),
                ('Bob', 30, 'bob@example.com'),
                ('Charlie', 35, 'charlie@example.com')
        ''')
        conn.execute(insert_query)
        conn.commit()

# Create and insert data
create_table(source)
insert_data(source)

# Read Data 
df = pd.read_sql('SELECT * FROM public.users', source)

# Filter data
date_threshold = datetime.now().date()
df['created_date'] = pd.to_datetime(df['created_date']).dt.date
filtered_df = df[df['created_date'] == date_threshold]

# Insert on target
filtered_df.to_sql('patients', target, if_exists='replace', index=False)