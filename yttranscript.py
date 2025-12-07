import yt_dlp
import os
import re
import webvtt
import pysrt
import sys
from commonfunctions import ai_youtube_summary_mainideas, get_youtube_urls
from configparser import ConfigParser

config = ConfigParser()
config.read("assistantconfig.ini")

outputpath = config["DEFAULTS"]["transcriptdownloadoutpath"]
videooutputpath = config["DEFAULTS"]["ytvideooutputpath"]
basepath = config["DEFAULTS"]["basepath"]
summarypath = config["DEFAULTS"]["summarypath"]
transcriptpath = config["DEFAULTS"]["yttranscriptpath"]
usedlinkspath = config["DEFAULTS"]["usedvideolinkspath"]

def generate_subtitle_file(link: str, summarize: str) -> list:
	# os.system(f'yt-dlp --cookies-from-browser firefox --skip-download --write-subs --write-auto-subs --sub-lang en --sub-format ttml --convert-subs srt --output "C:\Users\geoha\Documents\Python Projects\Ai Assistant\transcript.%(ext)s" {link}') # Uses yt-dlp.exe instead of module
	# title = os.system(f"yt-dlp --get-title {link}")	
	link = link.strip(" ")
	newlink = get_youtube_urls(link)

	yt_opts = {
		'writeautomaticsub': True,
		'writesubtitles': True,
		'skip_download': True,
		"cookiesfrombrowser": ('firefox', ),
		"subtitlesformat": "vtt",
		"outtmpl": outputpath,
		"consoletitle": True,
		# "quiet": True,
		"no_warnings": True,	
	}

	with open(usedlinkspath, "r") as f:
		usedlinks = f.readlines()

	if isinstance(newlink, list):
		print(newlink)
		with yt_dlp.YoutubeDL(yt_opts) as ydl:
			info = ydl.extract_info(link, download=False)
			playlisttitle = info.get("title", None)
			isplaylist = True
		for l in newlink:
			if link not in usedlinks:
				with yt_dlp.YoutubeDL(yt_opts) as ydl:
					ydl.download(l)
					info = ydl.extract_info(l, download=False)
					title = info.get('title', None)
					author = info.get('uploader', None)
				
				generate_transcript_as_clean_text(link, summarize, title, author, playlisttitle, isplaylist)

			else:
				print(f"Link {link} has already been downloaded\n")

	else:
		playlisttitle = ''
		isplaylist = False
		
		if link not in usedlinks:
			with yt_dlp.YoutubeDL(yt_opts) as ydl:
					ydl.download(link)
					info = ydl.extract_info(newlink, download=False)
					title = info.get('title', None)
					author = info.get('uploader', None)

			generate_transcript_as_clean_text(link, summarize, title, author, playlisttitle, isplaylist=False)	
		else:
			print(f"Link {link} has already been downloaded\n")
	# videoid = link[33:] # gets rid of the https:www.youtube.com/watch?v= leaving the key behind
	return title, author

def generate_transcript_as_clean_text(link: str, summarize: str, title: str, author: str, playlisttitle: str, isplaylist: bool) -> None:
	global subs, text, response_length

	filelist = os.listdir("/home/geohadg/Documents/")
	target = [f for f in filelist if f.endswith(".vtt")]
    
	vtt = webvtt.read(f"{basepath}/Documents/YoutubeTranscripts/temp.en.vtt")
	vtt.save_as_srt(f"{basepath}transcripts.en.srt")
	previous = None
	subs = pysrt.open(f'{basepath}transcripts.en.srt', encoding="utf-8")
	rawtext = [sub.text for sub in subs]
	text = []
	for line in rawtext:
		text.extend(line.split('\n'))

	rawtext[:] = text
	text = ''
	
	filelist = os.listdir(transcriptpath)
	title = ''.join(i for i in title if i.isalnum())
	if author not in filelist:
		os.mkdir(f"{transcriptpath}/{author}")

	if isplaylist:
		newpath = f"{transcriptpath}/{author}/{playlisttitle.strip("?")}"
		dirlist = os.listdir(f"{transcriptpath}/{author}")
		if playlisttitle not in dirlist:
			os.mkdir(newpath)

	else:
		newpath = f"{transcriptpath}/{author}"

	with open(f"{newpath}/{title}-transcript.txt", "w", encoding="utf-8") as nf:
		nf.write(f"{title} | TRANSCRIPT \n--------------------------------------------------------------------------\n")
		for line in rawtext:
			if line == previous:
				continue
		
			previous = line
			line = re.sub(r'\b\b;', '', line)
			line = re.sub('&nbsp', '', line)
			line = re.sub(r'\b\b;', '', line)
			text += line
			
			nf.write(f"{line}\n")

		nf.close()

	print(f"Finished Producing Transcript for {title}: by {author}")	
	try:
		os.remove(f"{basepath}/Documents/YoutubeTranscripts/temp.en.vtt")

	except:
		pass
			  
	print("\n--------------------------------------------------\n")

	# text = [t+'\n' for t in text]
	title = ''.join(i for i in title if i.isalnum())
	author = ''.join(i for i in author if i.isalnum())
	if summarize == "summarize": 
		try:
			ai_youtube_summary_mainideas(title, author, text, playlisttitle, isplaylist)

		except Exception as e: 
			print(f"Model Failed: {e}") # llama2 has a query limit of 4096 characters 
			pass

if __name__ == "__main__":
	if len(sys.argv) > 2 and sys.argv[2] == 'summarize':
		generate_subtitle_file(sys.argv[1], sys.argv[2])
			
	else:
		generate_subtitle_file(sys.argv[1], "n")
			
