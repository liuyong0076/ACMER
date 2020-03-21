import requests
from bs4 import BeautifulSoup
from io import BytesIO
import base64
import logging
from .models import CodeforcesQuestion,Contest
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

def getQuestion(cid,li):
    url = "https://codeforces.com/contest/"+str(cid)+"/problem/"+str(li['index'])
    html = getUrlText(url).replace('<br />', '\n').replace('</p>', '\n')
    soup = BeautifulSoup(html,"lxml")
    taglist = tagGet(soup)
    tags = ""
    difficulty = -1
    for tag in taglist:
        if tags =="":
            tags += tag
        else:
            tags += ","+tag
        if "*" in tag:
            difficulty = int(tag.split("*")[1])
    content = FindInfo(soup,url)
    return {'cid':int(cid),'name':li['name'],'content':content,'index':li['index'],"tags":tags,"difficulty":difficulty}

def FindInfo(soup,url):
    AllInfo = soup.find('div', {'class', 'problemindexholder'})
    content = ''
    imgs = AllInfo.find_all("img")
    for img in imgs:
        imurl = img['src']
        r = requests.get(imurl, stream=True)
        byt = BytesIO(r.content).getvalue()
        b64 = str(base64.b64encode(byt)).split("'")[1]
        father = img.parent
        if father.name == "center":
            father.name = "p"
        mkp = ("![avatar]("+"data:image/png;base64,"+str(b64)+")\n")
        father.append(mkp)
    divs = AllInfo.find_all('div')
    title = '## ' + divs[3].get_text()
    content +=('%s\n' % title)
    timelimit = "##### time limit: " + divs[4].get_text().split("test")[1]
    content += ('%s\n' % timelimit)
    memory = "##### memory limit: " + divs[6].get_text().split("test")[1]
    content += ('%s\n' % memory)
    problem = '### Description:\n' + divs[12].get_text()
    problem = Clear(problem)
    content +=('%s\n' % problem)
    Input = '### Input:\n' + divs[13].get_text()[5:]
    Input = Clear(Input)
    content +=('%s\n' % Input)
    Output = '### Output\n' + divs[15].get_text()[6:]
    Output = Clear(Output)
    content +=('%s\n' % Output)
    try:
        Sample = soup.find('div', {'class', 'sample-test'})
        SampleInputs = Sample.find_all('div', {'class', 'input'})
        SampleOutputs = Sample.find_all('div', {'class', 'output'})
        for i in range(len(SampleInputs)):
            SampleInput = SampleInputs[i].get_text()
            SampleOutput = SampleOutputs[i].get_text()
            content +=('## Sample Input:\n%s\n' % SampleInput[5:])
            content +=('## Sample Output:\n%s\n' % SampleOutput[6:])
    except:
        pass
    try:
        note = soup.find('div',{'class',"note"})
        Note = '## Note:\n'+note.get_text()[4:]
        Note = Clear(Note)
        content +=('%s\n' %(Note))
    except:
        pass
    content +=('### [题目链接](%s)\n\n' % url)
    return content

def tagGet(soup):
    taglist = []
    tags = soup.select(".tag-box")
    for tag in tags:
        taglist.append(tag.text.split("\r\n")[1].strip())
    return taglist
def Clear(text):
    p = True
    while p :
        p= False
        try:
            index = text.index('$$$')
            text = text[:index] + text[index + 2:]
            p=True
        except:
            p=False
    return text

def getContestIndex(cid):
    url = "https://codeforces.com/contest/"+str(cid)
    html = getUrlText(url)
    soup = BeautifulSoup(html,"lxml")
    tb = soup.select(".problems")[0]
    trs = tb.select("tr")
    datalist=[]
    for ids,tr in enumerate(trs):
        if ids !=0:
            tds = tr.select("td")
            index = tds[0].select("a")[0].text.split("\r\n")[1].replace(" ","")
            name = tds[1].find("a").text
            datalist.append({
                'name':name,
                'index':index,
            })
    return datalist

def getContestQuestion(cid,con):
    log = logging.getLogger("log")
    log.info("start get question" + str(cid))
    indexlist = getContestIndex(cid)
    datalist = []
    cname = con.cname
    con.questionnum = len(indexlist)
    con.save()
    for q in indexlist:
        log.info("start index" + q['index'])
        if CodeforcesQuestion.objects.filter(cid=cid,index=q['index']).count()==0:
            datalist.append(getQuestion(cid,q))
    for data in datalist:
        CodeforcesQuestion.objects.create(cid=data['cid'],cname = cname,name = data['name'],index = data['index'],tags = data['tags'],mdtext=data['content'],difficulty=data['difficulty'])

def updateContestQuestion():
    cons = Contest.objects.filter(ctype="cf")
    strs = ""
    for con in cons:
        if CodeforcesQuestion.objects.filter(cid = con.cid).count()<con.questionnum:
            strs += str(con.cid)+con.cname+","
            getContestQuestion(con.cid,con)
        elif con.questionnum == 0:
            strs += str(con.cid)+con.cname+","
            getContestQuestion(con.cid,con)
    return strs
