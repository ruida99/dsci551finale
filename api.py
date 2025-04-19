from openai import OpenAI
import pandas as pd
from sqlalchemy import create_engine
import sys
import pymysql
client = OpenAI(api_key=open("key.txt", "r").read())

def set_up():
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "user", "content":"can you write me sql code which returns me all my column names in my database from all tables"},
            {"role": "system",
             "content": "you are a database query generator which only returns the desired db query with nothing else"}
        ]
    )
    engine = create_engine('mysql+pymysql://root:NewPassword@localhost/Banking')
    sql = response.choices[0].message.content
    df = pd.read_sql(sql, engine)
    return df
def search_engin(message, df):
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "user", "content": message},
            {"role": "system", "content": f"you are a database query generator which only returns the desired db query with nothing else, and you know the database structure is {df.to_string(index=False)}"}
        ]
    )

    print(response.choices[0].message.content)
    engine = create_engine('mysql+pymysql://root:NewPassword@localhost/Banking')

    sql =  response.choices[0].message.content
    df = pd.read_sql(sql, engine)

    print(df)


if __name__ == "__main__":
    df = set_up()
    search_engin(sys.argv[1], df)