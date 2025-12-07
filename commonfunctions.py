import os
from pathlib import Path
import sys
from ollama import generate
import yt_dlp
from configparser import ConfigParser

pathstoskip = [
    r'C:\Users\geoha\Documents\Obsidian Notes\Mind Vault\3 - Tags', 
    r'C:\Users\geoha\Documents\Obsidian Notes\Mind Vault\5 - Templates'
    ]

config = ConfigParser()
config.read("assistantconfig.ini")

model = config["DEFAULTS"]["ollamamodel"]
summarypath = config["DEFAULTS"]["summarypath"]
basequery = config["DEFAULTS"]["basequeryprompt"]
baseytquery = config["DEFAULTS"]["baseytqueryprompt"]

files = []
types = [".pdf", ".txt", ".html"]

def getaisummary(text: str, title: str) -> None:
    print(f"{title}")
    response = generate(model=model, prompt=f"{basequery} {text}")
    print(response['response'])


def ai_youtube_summary_mainideas(title: str, author: str, text: str, playlisttitle: str, isplaylist: bool) -> None:	
    print(f"Prompting {model} for a summary...\n")
    filelist = os.listdir(summarypath)
    if author not in filelist:
        os.mkdir(f"{summarypath}{author}\\")

    if isplaylist:
        dirlist = os.listdir(f"{summarypath}{author}")
        newpath = f"{summarypath}{author}\\{playlisttitle}"
        if playlisttitle not in dirlist:
            os.mkdir(newpath)

    else:
        newpath = f"{summarypath}{author}"
	
    with open(f"{newpath}\\{title}-summary.txt", "w") as f:
        for part in generate(model=model, prompt=f"{baseytquery} {text}", stream=True):
            print(part['response'], end='', flush=True)
			
            f.write(part['response'])

    print(f"\n\n ---- Summary saved to {summarypath}{author}\\{title}-summary.txt")
    print("\n------------------------------------------------------------------------------------\n")

# def getfilelist(path=Path(".")) -> list:
#     path = Path(path)
#     files = []
#     for entry in Path.iterdir(path):
#         if entry.is_file():
#             files.append(os.path.abspath(entry))

#         if entry.is_dir() and entry not in pathstoskip:
#             getfilelist(entry)

#     return files

def getfilelist(path=Path(".")) -> list:
    
    for entry in Path.iterdir(path):
        if entry.is_file():
            for i in types:
                if str(entry).endswith(i):
                    
                    files.append(os.path.abspath(entry))

        if entry.is_dir():
            getfilelist(Path(r"{}".format(str(entry))))

    return files

def get_youtube_urls(url):
    yt_opts = {
        "skipdownload": "True",
        "flat-playlist": "True",
        "extract-flat": "True",
        "quiet": "True",
        "no_warnings": "True" 

    }
    with yt_dlp.YoutubeDL(yt_opts) as ydl:
        result = ydl.extract_info(url, download=False)
        if 'entries' in result:
            video_urls = [entry['webpage_url'] for entry in result['entries']]
            # print(video_urls)
            return video_urls
            

        else:
            # print(result['webpage_url'])
            return [result['webpage_url']]
