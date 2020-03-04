#计蒜客模块
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from .models import Student, Contest, StudentContest,AddStudentqueue,studentgroup,CFContest,Contestforecast,AddContestprize,Weightrating
import time
def getUrlText(url):
    while True:
        try:
            html = requests.get(url)
            html = html.text
            break
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            time.sleep(3)
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            time.sleep(3)    
        except:
            print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
            time.sleep(3)
    return html
def jskgetdata(jskID):
    url = 'https://i.jisuanke.com/u/'+jskID+'#contest'
    op = Options()
    op.add_argument('--headless')
    op.add_argument('--disable-gpu')
    op.add_argument("--no-sandbox")
    driver = webdriver.Chrome(chrome_options=op)
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source,"lxml")
    driver.close()
    datalist=[]
    try:
        tb=soup.select("table")[0]
        l = tb.select('tr')
    except:
        return datalist
    for n,tr in enumerate(l):
        if n !=0 :
            tds = tr.select("td")
            cname = tds[1].text
            rank = tds[3].text
            if rank == '-':
                rank = '999999'
            else:
                rank = rank.split("/")[0]
            cid = tds[1].select('a')[0]['href'].split("/")[4]
            solve = tds[2].text.split("/")[0]
            datalist.append({
                'time':'',
                'cname':cname,
                'cid':int(cid),
                'solve':solve,
                'rank':int(rank),
            })
    for data in datalist:
        cont = Contest.objects.filter(cid=data['cid'],ctype='jsk')
        if len(cont)==0:
            timestamp = jskgettime(data['cid'])
            data['time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp))
            Contest.objects.create(cid=data['cid'],cname=data['cname'],cdate=data['time'],starttimestamp=timestamp,ctype='jsk',cnumber=0)
        else:
            data['time']=cont[0].cdate
    return datalist

def jskgettime(cid):
    url = 'https://www.jisuanke.com/contest/'+str(cid)
    html = getUrlText(url)
    soup = BeautifulSoup(html,'lxml')
    info = soup.select('.contest_info')[0]
    times = info.contents[0].split("：")[1]
    timestamp = time.mktime(time.strptime(times,"%Y 年 %m 月 %d 日 %H:%M"))
    return timestamp

def getjskdata(stu):
    datalist = []
    if stu.jskID:
        datalist = jskgetdata(str(stu.jskID))
        stu.jskTimes = len(datalist)
        for data in datalist:
            if len(StudentContest.objects.filter(cid=data['cid'],ctype='jsk',stuNO = stu.stuNO)) == 0:
                StudentContest.objects.create(stuNO = stu.stuNO,realName = stu.realName,className=stu.className,
                cid = data['cid'],cname = data['cname'],cdate=data['time'],cdiv = 0,ctype = 'jsk',rank=data['rank'],solve=data['solve'],newRating=0)
            else:
                pass
    else:
        stu.jskTimes=0
    stu.jskRating = 0 
    stu.save()
    return len(datalist)

"""if __name__ == '__main__':
    ID = '10r90e54'
    jskgetdata(ID)"""
