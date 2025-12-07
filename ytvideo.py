import yt_dlp
from pathlib import Path
import os
import shutil
import re
import webvtt
import pysrt
import sys
from commonfunctions import ai_youtube_summary_mainideas
from configparser import ConfigParser

config = ConfigParser()
config.read("assistantconfig.ini")

outputpath = config["DEFAULTS"]["transcriptdownloadoutpath"]
videooutputpath = config["DEFAULTS"]["ytvideooutputpath"]
basepath = config["DEFAULTS"]["basepath"]
summarypath = config["DEFAULTS"]["summarypath"]
usedvideolinkspath = config["DEFAULTS"]['usedvideolinkspath']

def generate_subtitle_file(link) -> list:
	# os.system(f'yt-dlp --cookies-from-browser firefox --skip-download --write-subs --write-auto-subs --sub-lang en --sub-format ttml --convert-subs srt --output "C:\Users\geoha\Documents\Python Projects\Ai Assistant\transcript.%(ext)s" {link}') # Uses yt-dlp.exe instead of module
	# title = os.system(f"yt-dlp --get-title {link}")
	yt_opts = {
		'writeautomaticsub': True,
		'writesubtitles': True,
		'skip_download': True,
		"cookiesfrombrowser": ('firefox', ),
		"subtitlesformat": "srt",
		"outtmpl": outputpath,
		"consoletitle": True,
		"quiet": True,
		"no_warnings": True,	
	}

	with yt_dlp.YoutubeDL(yt_opts) as ydl:
		ydl.download(link)
		info = ydl.extract_info(link, download=False)
		title = info.get('title', None)
		author = info.get('uploader', None)

	videoid = link[33:] # gets rid of the https:www.youtube.com/watch?v= leaving the key behind

	return videoid, title, author

def generate_transcript_as_clean_text(link: str, summarize: str) -> None:
	global subs, text, response_length
	
	videoid, title, author = generate_subtitle_file(link.strip(" "))

	filelist = os.listdir(basepath)
	target = [f for f in filelist if f.endswith(".vtt")]
	
	if target:
		vtt = webvtt.read(f"{basepath}{target[0]}")
		vtt.save_as_srt(f"{basepath}transcripts.en.srt")


	previous = None
	subs = pysrt.open(f'{basepath}transcripts.en.srt', encoding="utf-8")
	rawtext = [sub.text for sub in subs]
	text = ''
	
	for line in rawtext:
		if line == previous:
			continue
		
		previous = line
		line = re.sub(r'\b\b;', '', line)
		line = re.sub('&nbsp', '', line)
		line = re.sub(r'\b\b;', '', line)
		text += line
		
	shutil.move(f"{basepath}transcripts.en.srt", f"{videooutputpath}{author}\\{title}")
	
	try:
		os.remove(f"{basepath}transcripts.en.srt")
		os.remove(f"{basepath}{target[0]}")
		os.remove(f"{basepath}Temptranscript.en.vtt")

	except:
		pass
			  
	print("\n-------------------------------------------------------------------------\n")

	# text = [t+'\n' for t in text]
	
	
	if summarize == "summarize": # str True or False
		try:
			ai_youtube_summary_mainideas(title, text)
			

		except Exception as e: 
			print(f"Model Failed: {e}") # llama2 has a query limit of 4096 characters 
			pass
	

	del subs, text # deletes these variables from global scope to conserve memory
	
def downloadvideorequest(link: str, summarize: str) -> None:
	with open(usedvideolinkspath, 'r') as f:
		usedlinks = f.readlines()
		if link in usedlinks:
			print(f"Link: {link} has already been downloaded\n")
			return "Ledeldeldedlel"

	yt_opts = {
		"quiet": True,
		"consoletitle": True,
		"no_warnings": True,
		"cookiesfrombrowser": ("firefox", ),
		"merge_output_format": "mp4"

	}

	print(f"Downloading {link} ...")
	with yt_dlp.YoutubeDL(yt_opts) as ydl:
		info = ydl.extract_info(link, download=False)
		author = info.get('uploader', None)
		title = info.get('title', None)
		ydl.download(link)

	filelist = os.listdir()
	targetlist = os.listdir(videooutputpath)
	title = ''.join(i for i in title if i.isalnum())
	author = ''.join(i for i in author if i.isalnum())
	if author not in targetlist:
		os.mkdir(f"{videooutputpath}{author}")

	os.mkdir(f"{videooutputpath}{author}\\{title}")

	for f in filelist:
		if f.endswith((".mp4", ".mkv")):
			shutil.move(f, f"{videooutputpath}{author}\\{title}")

	generate_transcript_as_clean_text(link, summarize)
	
	with open(usedvideolinkspath, 'a') as f:
		f.write(f"{link}\n")

		
def downloadvideosfromfile(path: str, summarize: str):
	with open(f"{path}", "r") as f:
		links = f.readlines()

	with open(usedvideolinkspath, "r") as f:
		usedlinks = f.readlines()

	for link in links[:-1]:
		if link not in usedlinks:
			downloadvideorequest(link.strip("\n"), summarize)

		else:
			print(f"Link {link} has already been downloaded\n")
			return

if __name__ == "__main__":
	try:
		if len(sys.argv) > 2 and sys.argv[2] == 'summarize':
			if Path(sys.argv[1]).is_file():
				downloadvideosfromfile(sys.argv[1], sys.argv[2])
			
			else:
				downloadvideorequest(sys.argv[1], sys.argv[2])

		else:
			downloadvideorequest(sys.argv[1], "n")

	except Exception as e:
		print(e)
