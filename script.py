#! /usr/bin/env python

import urllib2
import re
import sys
import os, shutil
from urllib import unquote

baseurl = "http://www.djbooth.net/index/"

def get_url_text(url):
	req = urllib2.Request(url)
	req.add_header("User-Agent","' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3")
	response = urllib2.urlopen(req)
	text = response.read()
	response.close()
	return text

def get_url_data(url):
	req = urllib2.Request(url)
        req.add_header("User-Agent","' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3")
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        return data


def scrape_chart():
	html = get_url_text(baseurl+"music-charts/entry/C27")
	## Write Out RE
	theRE = "<div class=\"f-info\">.*?<h3><a href=\"(.*?)\".*?>(.*?)</a>"
	return re.findall(theRE,html,re.DOTALL)

## Grabs the Radio URL from the track summary page.  Returns None if there is a problem.
def scrape_radio_url(trackurl):
	html = get_url_text(trackurl)
	theRE = "href=\"(http://www.djbooth.net/index/tracks/radio/.*?)\".*?>"
	m = re.search(theRE,html,re.DOTALL)
	if m:
		return m.group(1)
	else:
		return None

def direct(filename,html):

	theRE = "file: '(.*?)',"
	m =  re.search(theRE,html,re.DOTALL)
	if m:
		mp3url = m.group(1)
	else:
		return None

	mp3data = get_url_data(mp3url)
	f = open(filename, "wb")
	f.write(mp3data)
	f.close()
	return filename

def youtube(filename,html):
	theRE = "www.youtube.com/embed/(.*?)\?"
	m = re.search(theRE,html,re.DOTALL)
	if m:
		youtubeid = m.group(1)
	else:
		return None

	html = get_url_text("http://www.youtube.com/watch?v="+youtubeid)
	
			
	theRE = "flashvars.*?\"(.*?)\""

	v = re.search(theRE,html,re.DOTALL).group(1)

	unescaped = unquote(unquote(v))

	theRE = "url=(http:[^:]*?)&fallback"
	url = re.search(theRE,unescaped,re.DOTALL).group(1)

	f = open("out","w")
	f.write(get_url_data(url))
	f.close()

	os.system("ffmpeg -i out out.wav")
	os.system("lame -V3 out.wav \""+filename+"\"")
	os.remove("out")
	os.remove("out.wav")
	return filename

def soundcloud(filename,html):
	## Grab iframe src string
	theRE = "<iframe .*?src=\"(http://w.soundcloud.com.*?)\""
	m = re.search(theRE,html,re.DOTALL)
	if m:
		playerurl =  m.group(1)
	else:
		return None
	## Unescape the GET url api.soundcloud.com/tracks/.... url
	theRE = "url=(.*?)&amp"
	dataurl = re.search(theRE,playerurl).group(1)
	dataurl = unquote(dataurl)

	## Fetch src url
	html = get_url_text(playerurl)
	## Look for the clientID  :"(.*?)":null,host:'//api.soundcloud.com"
	theRE = ".*:\"(.*?)\":null,host:\"//api.soundcloud.com"
	clientID = re.search(theRE,html,re.DOTALL).group(1)
	## Fetch the API.soundcloud.com/tracks/###/stream?client_id=###
	dataurl += "/stream?client_id="+clientID
	try:
		f = open(filename,"w")
		f.write(get_url_data(dataurl))
		f.close()
	except:
		return None
	## You will be redirected to the MP3 location

	return filename


def clear_media():
	try:
		shutil.rmtree("mp3s")
	except:
		print "No Mp3s DIR"
	try:
		shutil.rmtree("wavs")
	except:
		print "No Wave DIR"

	os.mkdir("mp3s")



## Get Search Results
top20 = scrape_chart()

print top20
## Clear Media Folders
clear_media()

for track in top20:
	trackname = track[1]
	trackurl = track[0]


	radiourl = scrape_radio_url(trackurl)
	if radiourl:
		radiohtml = get_url_text(radiourl)
	else:
		print "No Radio.  Skipping Track"
		continue

	#
	trackname = "mp3s/"+trackname+".mp3"
	print trackname

	if(direct(trackname,radiohtml)):
		print "Donwloaded Direct"
	elif (soundcloud(trackname,radiohtml)):
		print "Downloaded from Soundcloud"
	elif (youtube(trackname,radiohtml)):
		print "Downloaded from Youtube"
	else:
		print "Could not download track"




#for f in os.listdir("mp3s"):
#	print "Convert "+f+" to wave"
#	os.system("ffmpeg -i mp3s/"+f+" wavs/"+f+".wav") 


## Burn CD
#os.system("cdrecord -v -pad speed=8 dev=/dev/scd1 -dao -audio -swab wavs/*.wav")
## shutil.rmtree("mp3s")/(wavs)

