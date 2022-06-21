import requests
import os
import json
from datetime import datetime, timedelta, date
import telegram
import re
import sqlite3
from sqlite3 import Error

telegram_bot_token = ""
database_path = ""
twitter_token = ""
keyword_path = ""
chat_id_ = ""

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_cve(conn, cve):
    sql = ''' INSERT INTO cve(data)
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, [cve])
    conn.commit()
    return cur.lastrowid


def select_cve_by_keyword(conn, keyword):
    cur = conn.cursor()
    cur.execute("SELECT * FROM cve WHERE data LIKE ?", (f"%{keyword}%",))
    rows = cur.fetchall()

    for row in rows:
        send_text_message(f"Keyword: {keyword}\n{row[0]}")


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def create_url(user_id, start_date):
    # Change to the endpoint you want to collect data from
    search_url = "https://api.twitter.com/2/users/{}/tweets".format(user_id)

    #change params based on the endpoint you are using
    query_params = {'start_time': start_date,
                    'pagination_token': {}}
    return (search_url, query_params)


def connect_to_endpoint(url, headers, params, pagination_token=None):
    # params object received from create_url function
    params['pagination_token'] = pagination_token
    response = requests.request("GET", url, headers=headers, params=params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def send_text_message(message):
    try:
        if message.strip() != None or message.strip() != "":
            message = message.strip().replace(
                "[", "\[").replace("*", "\*").replace("_", "\_")
        telegram_notify = telegram.Bot(
            telegram_bot_token)
        telegram_notify.send_message(
            chat_id=chat_id_, text=message, parse_mode='Markdown')
    except Exception as ex:
        print(ex)
        pass


def main():
    database = db_path

    # create a database connection
    conn = create_connection(database)

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Doping CVE table if already exists.
    cursor.execute("DROP TABLE IF EXISTS CVE")

    #Creating table as per requirement
    sql = '''CREATE TABLE CVE(
    DATA TEXT NOT NULL
    )'''
    cursor.execute(sql)

    # Commit your changes in the database
    conn.commit()

    headers = create_headers(
        twitter_token)

    notify_keyword = open(keyword_path, "r")
    notify_keyword_list = notify_keyword.readlines()
    notify_keyword.close()

    current_time = datetime.now()

    start_time = (current_time - timedelta(hours=1)
                  ).strftime('%Y-%m-%dT%H:%M:%SZ')

    CVEnew_ID = "821806287461740544"

    url = create_url(CVEnew_ID, start_time)
    json_response = connect_to_endpoint(url[0], headers, url[1])
    json_response.pop('meta', None)

    if json_response:
        for item in json_response['data']:
            create_cve(conn, item['text'])

    # send_text_message(f"Hi cc")

    for keyword in notify_keyword_list:
        select_cve_by_keyword(conn,keyword.strip('\n'))


if __name__ == '__main__':
    main()
