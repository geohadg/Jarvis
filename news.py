from newsapi import NewsApiClient
import datetime as dt
from pprint import pprint
from configparser import ConfigParser
from pathlib import Path
import smtplib
import ssl
from email.message import EmailMessage
import os

configfile = Path("newsconfig.ini")

config = ConfigParser()
config.read(configfile)

api_key = config['DEFAULT']['newsapikey']

newsapi = NewsApiClient(api_key=api_key)

political_sources = config['DEFAULT']['political_sources']
financial_sources = config['DEFAULT']['financial_sources']
science_sources = config['DEFAULT']['science_sources']

domains = config['DEFAULT']['domains']
terms_of_interest = list(config['DEFAULT']['terms'].split(','))

address = config['DEFAULT']['emailaddress']
password = config['DEFAULT']['emailpassword']

def sendGmail(body: str, subject: str, from_address: str, to_address) -> None:
    
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address

    context = ssl.create_default_context()
    smtp_server = 'smtp.gmail.com'
    port = 465

    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(address, password)
            server.send_message(msg)
        
        print("Success!")

    except Exception as e:
        print(f"An Error has occured: {e}")

def get_pointsguy_headlines() -> list:
    
    today = dt.datetime.now().strftime("%Y-%m-%d")

    financeheadlines = newsapi.get_everything(
                                              language='en',
                                              from_param=(dt.datetime.now() - dt.timedelta(days=10)).strftime('%Y-%m-%d'),
                                              sort_by='relevancy',
                                              domains='thepointsguy.com'
                                              )

    pointsguy = [i for i in financeheadlines['articles'] if i['source']['name'] == "The Points Guy"]
    
    return pointsguy

def main() -> list:
    with open('usedlinks.txt', 'r') as file:
        usedlinks = file.readlines()

    links_just_used = []
    email = f""""""

    today = (dt.datetime.now() - dt.timedelta(days=10)).strftime("%Y-%m-%d")
    articles = []
    
    for term in terms_of_interest:
        data = newsapi.get_everything(
                domains=domains,
                from_param=today,
                q=term,
                language='en',
                )

        for article in data['articles'][:5]:
            if f"{article['url']}\n" in usedlinks:
                pass

            else:
                email += f"""====================\nTitle: {article['title']}\nAuthor: {article['author']}\nDescription: {article['description'][:80]}\n{article['url']}====================\n"""
                print(article)
                links_just_used.append(article['url'])

    with open('usedlinks.txt', 'a') as file:
        for link in links_just_used:
            file.write(link + "\n")
                
    sendGmail(body=email, subject=f"News for {dt.datetime.now().strftime('%d/%m/%Y')}", from_address=address, to_address=address)

    return articles

if __name__ == "__main__":
    main()

"""
financial-post
google-news
hacker-news
next-big-future
the-wall-street-journal
the-huffington-post
the-washington-post

Tech News
Science News
Natural Disasters
US Politics
Federal Resere Updates
Financial News for Banks I work with, and General News

"""
