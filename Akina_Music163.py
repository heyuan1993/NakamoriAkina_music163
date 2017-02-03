#encoding=utf8
'''
#project1: 中森明菜网易云评论排行
算法：提取明菜网易云的所有专辑，再提取评论排名
补充算法：搜索中森明菜，补充没有收在明菜自己专辑中的歌
'''
import requests
from bs4 import BeautifulSoup
import re,time
import os,json
import base64
from Crypto.Cipher import AES
from pprint import pprint

from numpy import random

import os
import numpy as np
import scipy.io as sio

import pandas as pd
from pandas import Series, DataFrame, ExcelWriter


import matplotlib.pyplot as plt

#导入结巴分词库(分词)
import jieba as jb
#导入结巴分词(关键词提取)
import jieba.analyse


work_path = 'D:\\Python_learning\\Project_5_akina_music163'
os.chdir(work_path)

headers_url = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Host':'music.163.com',
	'Referer':'http://music.163.com/',
	'Accept-Encoding':'gzip, deflate, sdch',
	'Accept-Language':'zh-CN,zh;q=0.8',
	'Connection':'keep-alive',
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}

Cookie = {
	'vjuids':'-143da5167.15213852819.0.22cc652',
	'_ga':'GA1.2.150505644.1453795981',
	'__utma':'187553192.150505644.1453795981.1475840589.1476693844.2',
	'__utmz':'187553192.1476693844.2.2.utmcsr=reg.163.com|utmccn=(referral)|utmcmd=referral|utmcct=/Main.jsp',
	'P_INFO':'xjtu_heyuan1993@163.com|1479418033|0|mail163|00&12|zhj&1479241048&mail_newmsg#DE&null#10#0#0|153690&0||xjtu_heyuan1993@163.com',
	'mail_psc_fingerprint':'1996502860',
	'_ntes_nnid':'336b163a9caa02dc7612abefabccaae6,1483565835627',
	'_ntes_nuid':'336b163a9caa02dc7612abefabccaae6',
	'vjlast':'1452026440.1485128861.22',
	'Province':'0',
	'City':'0',
	'vinfo_n_f_l_n3':'f748b405a5b65de1.1.5.1452026439832.1475138902077.1485128921735',
	'JSESSIONID-WYYY':'AX%2B%2BujDmGIY6fExmXSy8sm9OXWjKb9%2BK%2Fo3fFNvjiFc4hPBB9Bpg%5CXt4uywhuGCNYO7WSbkmfTZhTtDqP9I%5Cly3srODx6kNONO2SbDT1K%2FBXcYIdIH16afwCymyZr7HzPWVe382%5CWFwBgouf7lm7fhMI%5CbNOTtAMleoBQDy5g4Qvllhp%3A1485347679610',
	'_iuqxldmzr_':'32',
	'MUSIC_U':'858c57d80bb2718c5ba44bd89a7e5beffd01ef448e66cc155a3f35f07d348e03d50fc89769c88b63c0853538a7a760a84004e1d820104584bf8da49b6c1e801dbf122d59fa1ed6a2',
	'__csrf':'280fc5a01ec6d1bdeb86f8d2248ef036',
	'__remember_me':'true',
	'__utma':'94650624.7060989.1448799387.1485344141.1485346333.57',
	'__utmb':'94650624.9.10.1485346333',
	'__utmc':'94650624',
	'__utmz':'94650624.1479335405.41.7.utmcsr=baidu|utmccn=(organic)|utmcmd=organi'
}

Hot_50_URL = 'http://music.163.com/#/artist?id=17312'


'''
# this is the false url
(which display in the brower but do not have actual information): 
'http://music.163.com/#/artist/album?id=17312'
'''

# starting url: http://music.163.com/artist/album?id=17312&limit=12&offset=0
Akina_album = 'http://music.163.com/artist/album?id=17312'

class Song(object):
	def __lt__(self, other):
		return self.commentCount > other.commentCount

def getAlbumFromSinger(pageIndex):
	pageUrl = Akina_album + '&limit=12&offset=' + pageIndex
	r = requests.get(url=pageUrl, headers=headers_url, cookies=Cookie)
	html = r.content.decode()
	# attention: question mark ? need to add a slash \
	AlbumList = re.findall(r'<a href="/album\?id=(.*?)" class="tit f-thide s-fc0"',html)
	for i in AlbumList:
		print('albumID:'+i)
		getSongFromAlbum(i)
	time.sleep(random.uniform(4, 5))

def getSongFromAlbum(AlbumIndex):
	BASE_URL = 'http://music.163.com' + '/album?id='
	songListUrl = BASE_URL + AlbumIndex
	r = requests.get(url=songListUrl, headers=headers_url, cookies=Cookie)
	print('request: status' + str(r.status_code))
	html = r.content.decode()
	# album content information
	SongIDList =  re.findall(r'<li><a href="/song\?id=(.*?)">',html)
	#SongNameInAlbumList = re.findall(r'<a class="sname f-fs1 s-fc0" href="/album\?id=.*?" title="(.*?)">',html)
	ReleaseDate = re.findall(r'<b>发行时间：</b>(.*?)</p>',html) 
	AlbumName = re.findall(r'<h2 class="f-ff2">(.*?)</h2>',html)
	# album comment
	#http://music.163.com/weapi/v1/resource/comments/R_AL_3_35114313/ 
	for i in range(len(SongIDList)):
		SongID = SongIDList[i]
		#print(SongID)
		# save song informations
		SongIDs.append(SongID)
		ReleaseDates.append(ReleaseDate)
		AlbumNames.append(AlbumName[0])
		# get comments number from each song
		SongBase_URL = 'http://music.163.com/song?id='
		Song_URL = SongBase_URL + SongID
		comment, SongName  = readSongInfo(SongID)
		print(SongID + ',' +  SongName + ',' + str(comment))
		comments.append(comment)
		SongNames.append(SongName)
		time.sleep(random.uniform(1, 6))
	time.sleep(random.uniform(2, 4))
	#return SongIDs, AlbumNames, comments,ReleaseDates

def readSongInfo(SongID):
	headers = {
		'Host': 'music.163.com',
		'Connection': 'keep-alive',
		'Content-Length': '484',
		'Cache-Control': 'max-age=0',
		'Origin': 'http://music.163.com',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
		'Content-Type': 'application/x-www-form-urlencoded',
		'Accept': '*/*',
		'DNT': '1',
		'Accept-Encoding': 'gzip, deflate',
		'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
		'Cookie': 'JSESSIONID-WYYY=b66d89ed74ae9e94ead89b16e475556e763dd34f95e6ca357d06830a210abc7b685e82318b9d1d5b52ac4f4b9a55024c7a34024fddaee852404ed410933db994dcc0e398f61e670bfeea81105cbe098294e39ac566e1d5aa7232df741870ba1fe96e5cede8372ca587275d35c1a5d1b23a11e274a4c249afba03e20fa2dafb7a16eebdf6%3A1476373826753; _iuqxldmzr_=25; _ntes_nnid=7fa73e96706f26f3ada99abba6c4a6b2,1476372027128; _ntes_nuid=7fa73e96706f26f3ada99abba6c4a6b2; __utma=94650624.748605760.1476372027.1476372027.1476372027.1; __utmb=94650624.4.10.1476372027; __utmc=94650624; __utmz=94650624.1476372027.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
	}
	params = {
		'csrf_token': ''
	}
	data = {
		'params': 'Ak2s0LoP1GRJYqE3XxJUZVYK9uPEXSTttmAS+8uVLnYRoUt/Xgqdrt/13nr6OYhi75QSTlQ9FcZaWElIwE+oz9qXAu87t2DHj6Auu+2yBJDr+arG+irBbjIvKJGfjgBac+kSm2ePwf4rfuHSKVgQu1cYMdqFVnB+ojBsWopHcexbvLylDIMPulPljAWK6MR8',
		'encSecKey': '8c85d1b6f53bfebaf5258d171f3526c06980cbcaf490d759eac82145ee27198297c152dd95e7ea0f08cfb7281588cdab305946e01b9d84f0b49700f9c2eb6eeced8624b16ce378bccd24341b1b5ad3d84ebd707dbbd18a4f01c2a007cd47de32f28ca395c9715afa134ed9ee321caa7f28ec82b94307d75144f6b5b134a9ce1a'
	}
	headers['Referer'] = 'http://music.163.com/playlist?id=' + SongID
	comment_page = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + SongID
	r = requests.post(comment_page, headers=headers, params=params, data=data)
	total = r.json()['total'] 
	time.sleep(random.uniform(1, 2))
	songIDUrl = 'http://music.163.com/song?id='+ SongID
	r = requests.get(url=songIDUrl, headers=headers_url, cookies=Cookie)
	html = r.content.decode()
	# attention: question mark ? need to add a slash \
	SongName = re.findall(r'name="keywords" content="(.*?)，',html)[0]
	return total, SongName

def main():
	for i in range(0,10):
		getAlbumFromSinger(str(i*12))
		# 按评论数从高往低排序

	
if __name__ == '__main__':
	SongIDs=[]
	SongNames=[]
	AlbumNames=[]
	comments=[]
	ReleaseDates=[]
	main()
	data = {'专辑名':AlbumNames,'曲名':SongNames,'评论数':comments}
	songCommentsTable = pd.DataFrame(data)
data = {'专辑名':AlbumNames,'曲名':SongNames,'评论数':comments,'发行时间':ReleaseDates}
frame = pd.DataFrame(data)
model_name = '明菜网易云'
writer = ExcelWriter(model_name+'.xlsx')
xls_file = frame.to_excel(writer,'201701',startrow=2, startcol=2)
writer.save()

with open('song.json', 'w') as f:
    json.dump(data, f)