from openai import OpenAI
import pandas as pd
from sqlalchemy import create_engine
import sys
import pymysql
import pymongo
client = OpenAI(api_key=open("key.txt", "r").read())

def set_up():
    sql_root = 'mysql+pymysql://root:NewPassword@localhost/Banking'
    db_name = sql_root.split('/')[-1]
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "user", "content":f"can you write me sql code for Mysql which returns me all my column names in my database from all tables and my database name is {db_name}"},
            {"role": "system",
             "content": "you are a database query generator which only returns the desired db query with nothing else"}
        ]
    )
    engine = create_engine(sql_root)
    sql = response.choices[0].message.content
    df = pd.read_sql(sql, engine)
    return df

CONVERSATION_HISTORY = []

def set_up_mongo():
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    # List all databases
    databases = mongo_client.list_database_names()
    database_collections_string = ""
    for db_name in databases:
        database_collections_string += f"Database: {db_name}\n"
        # List all collections in the database
        db = mongo_client[db_name]
        collections = db.list_collection_names()
        for collection_name in collections:
            database_collections_string += f"  Collection: {collection_name}\n"
    # print(database_collections_string)
    # print("Databases:")
    # for db_name in databases:
    #     print(f"- {db_name}")
    #     # List all collections in the database
    #     db = mongo_client[db_name]
    #     collections = db.list_collection_names()
    #     print("  Collections:")
    #     for collection_name in collections:
    #         print(f"  - {collection_name}")
    
    CONVERSATION_HISTORY.append( {"role": "system", "content": "We are going to pass all database and collections in the database to you, please remember them"} )
    CONVERSATION_HISTORY.append({"role": "system", "content": database_collections_string} )
    response = client.chat.completions.create(
        
        model="gpt-4.1-nano",
        messages=CONVERSATION_HISTORY
    )

    print(response.choices[0].message.content)

def search_engin(message, df):
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "user", "content": message},
            {"role": "system", "content": f"you are a database query generator which only returns the desired db query with nothing else, and you know the database structure is {df.to_string(index=False)}"}
        ]
    )

    engine = create_engine('mysql+pymysql://root:NewPassword@localhost/Banking')
    sql =  response.choices[0].message.content
    respond = pd.read_sql(sql, engine)
    print(respond)


if __name__ == "__main__":
    df = set_up()
    search_engin(sys.argv[1], df)

    # response = client.chat.completions.create(
    #     model="gpt-4.1-nano",
    #     messages=[
    #         {"role": "user", "content": "Hello World!"},
    #         # {"role": "system", "content": f"you are a database query generator which only returns the desired db query with nothing else, and you know the database structure is {df.to_string(index=False)}"}
    #     ]
    # )
    # print(response.choices[0].message.content)
    # Connect to the local MongoDB instance
    # mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    # # List all databases
    # databases = mongo_client.list_database_names()
    # print("Databases:")
    # for db_name in databases:
    #     print(f"- {db_name}")
    #     # List all collections in the database
    #     db = mongo_client[db_name]
    #     collections = db.list_collection_names()
    #     print("  Collections:")
    #     for collection_name in collections:
    #         print(f"  - {collection_name}")
    #set_up_mongo()
