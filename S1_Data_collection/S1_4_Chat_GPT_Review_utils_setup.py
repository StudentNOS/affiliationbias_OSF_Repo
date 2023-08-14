import sqlite3
import time
import openai
import pandas as pd
import ast
import json

# DB path is hardcoded here
db_path = "data_v2.sqlite"

    
def integrity_check():
    """Check if data is plausible.
    Prints all tables and their columns, as well as the number of rows in each table."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    #c.execute("PRAGMA foreign_keys = ON")
    # Select all tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print("Found tables:", tables)
    # Get column names for each table
    for table in tables:
        c.execute(f"PRAGMA table_info({table[0]})")
        print(f"Table {table[0]} has columns: {c.fetchall()}")
    # Get number of rows in each table
    for table in tables:
        c.execute(f"SELECT COUNT(*) FROM {table[0]}")
        print(f"Table {table[0]} has {c.fetchone()[0]} rows")
    conn.close()
    

def db_update(ix, field, value, table="gpt_completions"):
    """Update a single field in a row.
    Args:
        ix (int): Row id
        field (str): column name
        value (str): New value
        table (str): Table name
    Returns:
        None"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"UPDATE {table} SET {field} = ? WHERE id = ?", (value, ix))
    conn.commit()
    conn.close()
    
def db_update_multi(ix, fields_dict, table="gpt_completions"):
    """Update multiple fields in a row.
    Args:
        ix (int): Row id
        fields_dict (dict): {column_name: new_value}
        table (str): Table name
    Returns:
        None"""
    # # Convert dict values that are a dict to a string
    for k,v in fields_dict.items():
        if type(v) == dict:
            fields_dict[k] = json.dumps(v)
    fields_dict["meta"] = json.dumps(fields_dict["meta"])
       
    # for each key get key = ?
    col_names = ",".join([f"{k} = ?" for k in fields_dict.keys()])
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # query var for debugging only
    query = f"UPDATE {table} SET {col_names} WHERE id = {ix}", list(fields_dict.values())
    c.execute(query[0], query[1])
    #c.execute(f"UPDATE {table} SET {fields} WHERE id = {ix}")
    conn.commit()
    conn.close()
    print(f"Updated row id {ix} in table {table}")

def db_delete(ix, table="gpt_completions"):
    """Delete a row.
    Args:
        ix (int): Row id
    Returns:
        None"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"DELETE FROM {table} WHERE id = {ix}")
    conn.commit()
    conn.close()
    print(f"Deleted row id {ix} from table {table}")
    
def db_query(condition,fields="*",table="gpt_completions"):
    """Query the database.
    Args:
        condition (str): SQL condition (where clause)
        fields (str): Comma separated list of fields to return
        table (str): Table name
    Returns:
        results (list): List of tuples with results"""
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query = f"SELECT {fields} FROM {table} where " + condition
    #print(query)
    c.execute(query)
    results = c.fetchall()
    conn.close()
    return results

def db_insert(fields, values, table="gpt_completions"):
    """Insert a row.
    Args:
        fields (list): List of column names
        values (list): List of values
        table (str): Table name
    Returns:
        row_id (int): Row id of inserted row"""
    conn = sqlite3.connect("data_v2.sqlite")
    c = conn.cursor()
    str_fields = ",".join(fields)
    str_values = ",".join(["?" for e in values])
    c.execute(f"INSERT INTO {table} ({str_fields}) VALUES ({str_values})", values)
    row_id = c.lastrowid
    print(f"Inserted row id {row_id} into table {table}")
    conn.commit()
    conn.close()
    return row_id

def create_emptydb():
    """Create an empty database.
    CAREFUL - this will delete the existing database."""
    
    # Use SQLite to store results
    # Caution - this will delete the existing database
    confirmation = input(f"Warning - {db_path} will be deleted. Are you sure? Press y to continue ")
    assert confirmation == "y", "Aborted"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("Drop table if exists abstracts")
    c.execute("""
        CREATE TABLE IF NOT EXISTS abstracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        abstract TEXT,
        date TEXT,
        author_list TEXT,
        journal TEXT,
        doi TEXT)""")
    c.execute("Drop table if exists gpt_completions")
    c.execute("""
        CREATE TABLE IF NOT EXISTS gpt_completions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        abstract_id INTEGER FOREIGNKEY REFERENCES abstracts(id),
        prompt_id INTEGER,
        blinded INTEGER,
        gpt_accept INTEGER,
        category_scores TEXT,
        meta TEXT
        )""")
    conn.commit()
    conn.close()

def generate_completion(prompt, blinded, title, abstract, author=""):
    """Generate a completion using OpenAI's API.
    Args:
        prompt (str): Prompt to send to API as system message
        blinded (bool): Whether to include author details in prompt
        title (str): Title of abstract
        abstract (str): Abstract text
        author (str): Author details
    Returns:
        completion (dict): Completion from API"""
    msg = ""
    if not blinded:
        msg += f"Author: {author} \n"
    
    msg += f"Title: {title} \n Abstract: {abstract}"
    
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = [
                {"role":"user", "content": msg},
                {"role":"system", "content": prompt}
            ],
            max_tokens=200,
            n=1,
            temperature=1
        )
    except Exception as e:
        print(f"---error--- Skipping and waiting for 5 seconds. ({e})")
        time.sleep(5)
        completion = -1
        
    return completion



def reset_table_abstracts():
    """Reset the abstracts table."""
    create_emptydb()
    df = pd.read_csv("src/data.csv",sep=";")
    df["author_details_parsed"] = ""

    drop_rows = []

    # Clean up author details
    for i, e in df.iterrows():
        try:
            auth_list = ast.literal_eval(e["author_details"])
            df.loc[i,"author_details_parsed"] = json.dumps(auth_list)
        except:
            print("ERROR at index", i)
            print(e["author_details"])
            drop_rows.append(i)
            continue
    df = df.drop(drop_rows)
    
    # Add data from the dataframe to the database
    conn = sqlite3.connect("data_v2.sqlite")
    c = conn.cursor()
    for i, e in df.iterrows():
        first_author = json.dumps(json.loads(e["author_details_parsed"])[0][2:6])
        c.execute("""INSERT INTO abstracts (title, abstract, date, author_list, journal, doi) VALUES (?, ?, ?, ?, ?, ?)""", (e["title"], e["abstract"], e["date"], first_author, e["journal"], e["doi"]))
    conn.commit()
    conn.close()

    
    
def parse_result(completion,ix_prompt, blinded):
    """Parse the result from the API.
    Args:
        completion (dict): Completion from API
        ix_prompt (int): Prompt id
        blinded (bool): Whether author details were included in prompt
    Returns:
        result_dict (dict): Parsed result"""
    try:
        if ix_prompt == 1:
                result_dict = {
                    "prompt_id": ix_prompt,
                    "blinded": blinded,
                    "gpt_accept": int(completion.choices[0].message['content']),
                    "category_scores": 999,
                    "meta": completion
                }
        elif ix_prompt == 2:
            result_dict = {
                "prompt_id": ix_prompt,
                "blinded": blinded,
                "gpt_accept": json.loads(completion.choices[0].message['content'])["overall_decision"],
                "category_scores": json.loads(completion.choices[0].message['content']),
                "meta": completion
            }
        elif ix_prompt == 4:
            result_dict = {
                "prompt_id": ix_prompt,
                "blinded": blinded,
                "gpt_accept": json.loads(completion.choices[0].message['content'])["overall_decision"],
                "category_scores": json.loads(completion.choices[0].message['content']),
                "meta": completion
            }
        elif ix_prompt == 5:
            result_dict = {
                "prompt_id": ix_prompt,
                "affil_tested": blinded,
                "gpt_accept": json.loads(completion.choices[0].message['content'])["overall_decision"],
                "category_scores": json.loads(completion.choices[0].message['content']),
                "meta": completion
            }
        else:
            raise Exception(f"Invalid prompt id {ix_prompt}. New prompts must be defined in utils.py -> parse_result()")
    except:
        result_dict = {
        "prompt_id": ix_prompt,
        "blinded": blinded,
        "gpt_accept": 998,
        "category_scores":998,
        "meta": completion
        }
        print(f"ERROR parsing {completion} - saving as 998")
    
        
    return result_dict


def counter(list, ix_pr, blind):
    # Deprecated
    count = 0
    for e in list:
        if e["prompt_id"] == ix_pr and e["blinded"] == blind:
            count += 1
    return count


def get_timestamp():
    """Return current time in format YYYY-MM-DD HH:MM:SS"""
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())