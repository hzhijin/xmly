import requests,hashlib,time,random
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

pd.options.display.max_columns = 50

def xm_md5():
    url = 'https://www.ximalaya.com/revision/time'
    headrer = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
            'Host': 'www.ximalaya.com'}
    html = requests.get(url, headers = headrer)
    nowTime = str(round(time.time()*1000)) #13位时间戳
    sign = str(hashlib.md5("himalaya-{}".format(html.text).encode()).hexdigest()) + "({})".format(str(round(random.random()*100))) + html.text + "({})".format(str(round(random.random()*100))) + nowTime
    return sign

def getAudio(trackId,title):
	url = 'https://www.ximalaya.com/revision/play/v1/audio?id='+str(trackId)+'&ptype=1'
	headers = {
		'Host':'www.ximalaya.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
		'Accept':'*/*',
		'Accept-Language':'en-US,en;q=0.5',
		'Accept-Encoding':'gzip, deflate, br',
		'xm-sign':xm_md5(),
		'Connection':'keep-alive',
	}
	r = requests.get(url = url,headers = headers).json()['data']['src']
	r = requests.get(r)
	
	with open(title + '.m4a','wb') as f:
		f.write(r.content)
	return True

def getTracksList(albumId,pageNum=1):
	url = 'https://www.ximalaya.com/revision/album/v1/getTracksList?albumId='+str(albumId)+'&pageNum='+str(pageNum)
	headers = {
		'Host':'www.ximalaya.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
		'Accept':'*/*',
		'Accept-Language':'en-US,en;q=0.5',
		'Accept-Encoding':'gzip, deflate, br',
		'xm-sign':xm_md5(),
		'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
		'Connection':'keep-alive',
	}
	r = requests.get(url = url,headers = headers).json()['data']['tracks']
	df = pd.DataFrame(r)
	return df


def getChannelList(cNum):
	url = 'https://www.ximalaya.com/channel/' + str(cNum)
	headers = {
		'Host':'www.ximalaya.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Language':'en-US,en;q=0.5',
		'Accept-Encoding':'gzip, deflate, br',
		'Connection':'keep-alive',
	}
	r = requests.get(url=url,headers=headers)
	
	b = BeautifulSoup(r.content,'lxml')
	
	aList = b.findAll('a',{'class':'album-title line-2 lg bold kF_'})
	res = []
	for a in aList:
		albumId = a.attrs['href'].split('/')[-2]
		title = a.attrs['title']
		res.append((albumId,title))
	
	df = pd.DataFrame(res,columns = ['albumId','title'])
	return df

cNum = 18
dfc = getChannelList(cNum)
for i in tqdm(range(2)):
	albumId = dfc.iloc[i]['albumId']
	df = getTracksList(albumId,pageNum=1)
	for j in range(3):
		trackId = df.iloc[j]['trackId']
		title = df.iloc[j]['title']
		getAudio(trackId,title)
		print(df.head())


