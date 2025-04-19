from openai import OpenAI
import pandas as pd
from sqlalchemy import create_engine, text
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
TARGETED_MONGO_DB = "lab3"

def set_up_mongo():
    # choose database
    TARGETED_MONGO_DB = input ("Enter the name of the database you want to target: ")
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    # List all databases
    databases = mongo_client.list_database_names()
    database_collections_string = ""
    for db_name in databases:
        database_collections_string += f"Database: {db_name}\n"
        # List all collections in the database
        dibi = mongo_client[db_name]
        collections = dibi.list_collection_names()
        for collection_name in collections:
            database_collections_string += f"  Collection: {collection_name}\n"
    mongo_client.close()
    
    # pass it into ChatGPT
    CONVERSATION_HISTORY.append( {"role": "system", "content": "We are going to pass all database and collections in the database to you, please remember them"} )
    CONVERSATION_HISTORY.append({"role": "system", "content": database_collections_string} )

    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")

    databases = mongo_client.list_database_names()
    database_collections_string = ""
    for db_name in databases:
        database_collections_string += f"Database: {db_name}\n"
        dibi = mongo_client[db_name]
        collections = dibi.list_collection_names()
        # grab an example for the context
        for collection_name in collections:
            document = dibi[collection_name].find_one()
            CONVERSATION_HISTORY.append({"role": "system", "content": f" Here is an example docment in Collection: {collection_name}: {document}\n"})
    mongo_client.close()

    CONVERSATION_HISTORY.append({"role": "system", "content": "in particular, we will focus on database " +TARGETED_MONGO_DB } )
    # CONVERSATION_HISTORY.append({"role": "system", "content": "We are going to pass you the code of the api.py file, please remember it."} )
    # CONVERSATION_HISTORY.append({"role": "system", "content": "The code is as follows:"} )
    # with open("api.py", "r") as f:
    #     code = f.read()
    #     CONVERSATION_HISTORY.append({"role": "system", "content": code } )
    #     f.close()
    # CONVERSATION_HISTORY.append({"role": "system", "content": "Here is an example of what a comment looks like in comments: "+ COMMENTS_EXAMPLE} )
    # CONVERSATION_HISTORY.append({"role": "system", "content": "Here is an example of what a movie looks like in movies: "+ MOVIES_EXAMPLE} )

    CONVERSATION_HISTORY.append({"role": "system", "content": "From now on we are going to pass human input, and for the output we expect precisely executable python pymongo (i.e. runnable with exec() in python) code without markup to query the databases and tables. We want the python code to print expected results."} )
    response = client.chat.completions.create(
        
        model="gpt-4.1-mini",
        messages=CONVERSATION_HISTORY
    )

    print(response.choices[0].message.content)
    CONVERSATION_HISTORY.append({"role": "assistant", "content": response.choices[0].message.content})
    # print(CONVERSATION_HISTORY)
def run_commands():
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    mongo_targeted_db = mongo_client[TARGETED_MONGO_DB]
    while True:
        user_input = input("Enter your command (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        #TODO: consider adding mongodb query for show
        CONVERSATION_HISTORY.append({"role": "system", "content": "Remember: for the output we expect precisely executable python pymongo (i.e. runnable with exec() in python) code without markup to query the databases and tables. We want the python code to print expected results."} )

        CONVERSATION_HISTORY.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=CONVERSATION_HISTORY
        )
        print("###### PROPOSED CODE ######\n" + response.choices[0].message.content + "\n####### PROPOSED CODE #######")
        exec_code = response.choices[0].message.content
        if exec_code.startswith("```python"):
            exec_code = exec_code[9:].strip()
        if exec_code.endswith("```"):
            exec_code = exec_code[:-3].strip()
        if exec_code.startswith("```"):
            exec_code = exec_code[3:].strip()
        # TODO: see if code compiles
        # try:
        #     compile(code_string, '<string>', 'exec')
        #     return True
        # except SyntaxError:
        #     return False
        print("###### BEGIN OUTPUT ######\n")
        try:
            exec(exec_code)
        except Exception as e:
            print(f"Error executing command: {e}")
        print("\n####### #END OUTPUT# #######")
        CONVERSATION_HISTORY.append({"role": "assistant", "content": response.choices[0].message.content})

def search_engin():
    history = []
    dbs = set_up()
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "user", "content": f"remember the database structure is {dbs.to_string(index=False)}"},
            {"role": "system",
             "content": f"you are a database query generator which only returns the desired sql query with nothing else."}
        ]
    )
    history.append({"role": "user", "content": f"remember the database structure is {dbs.to_string(index=False)}"})
    history.append({"role": "system",
             "content": f"you are a database query generator which only returns the desired sql query with nothing else."})
    history.append({"role": "assistant","content": response.choices[0].message.content})
    while True:
        message = input("Enter your message: ")
        if message.lower() == "exit":
            break
        history.append({"role": "system", "content": message})
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=history)
        history.append({"role": "assistant", "content": response.choices[0].message.content})
        engine = create_engine('mysql+pymysql://root:NewPassword@localhost/Banking')
        sql =  response.choices[0].message.content
        if sql.startswith("```sql"):
            sql = sql[6:].strip()
        if sql.endswith("```"):
            sql = sql[:-3].strip()
        if sql.startswith("```"):
            sql = sql[3:].strip()
        try:
            if (sql.strip().upper().startswith("INSERT") or sql.strip().upper().startswith("UPDATE")
                    or sql.strip().upper().startswith("DELETE") or sql.strip().upper().startswith("CREATE")
                    or sql.strip().upper().startswith("DROP")):
                with engine.connect() as conn:
                    conn.execute(text(sql))
                    conn.commit()
                    print("Query executed successfully.")
            else:
                respond = pd.read_sql(sql, engine)
                print(respond)
        except Exception as e:
            print(f"query failed because of {e}")




if __name__ == "__main__":
    while True:
        database_choice = input("choose a database to query (sql or mongo or exit): ")
        if database_choice.lower() == "exit":
            break
        if database_choice.lower() == "sql":
            search_engin()
        elif database_choice.lower() == "mongo":
            set_up_mongo()
            run_commands()
