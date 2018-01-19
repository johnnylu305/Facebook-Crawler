import requests
import json
import re
import time
import random

count=1
page=""
token=""
since=""
until=""
T=0
def getUntil():
    f=open(page+"/until","r") 
    until=f.readline()
    f.close()
    return until

def getSince():
    f=open(page+"/since","r") 
    since=f.readline()
    f.close() 
    return since

def updateUntil(until):
    f=open(page+"/until","w")    
    f.write(until)
    f.close()

def getUrl():
    global token
    global page
    until=getUntil()
    since=getSince()
    like="reactions.type(LIKE).limit(0).summary(total_count).as(like)"
    love="reactions.type(LOVE).limit(0).summary(total_count).as(love)"
    haha="reactions.type(HAHA).limit(0).summary(total_count).as(haha)"
    wow="reactions.type(WOW).limit(0).summary(total_count).as(wow)"
    sad="reactions.type(SAD).limit(0).summary(total_count).as(sad)"
    angry="reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
    reaction=like+','+love+','+haha+','+'wow'+','+'sad'+','+angry
    fields="posts.limit(1).since("+since+").until("+until+"){updated_time,created_time,message,"+reaction+",comments.limit(100)}"
    return "https://graph.facebook.com/v2.10/"+page+"?access_token="+token+"&fields="+fields 

def getData(url):
    res=requests.get(url)
    data=json.loads(res.text)
    return data

def getTime(post):
    for p in post['data']:
        upTime=p['updated_time']
        crTime=p['created_time']
    return upTime[0:upTime.find('+')],crTime[0:crTime.find('+')]    

def updateSince(time):
    global since
    l=nextSince(time)
    for i in xrange(1,6):
        if len(l[i])==1:
            l[i]='0'+l[i]
    oldSince=l[0]+'-'+l[1]+'-'+l[2]+'T'+l[3]+':'+l[4]+':'+l[5]
    if oldSince[0:19]<since[0:19]:
        oldSince=since
    f=open(page+"/since",'w')
    f.write(oldSince)
    f.close()


def nextSince(time):
    month=[0,31,28,31,30,31,30,31,31,30,31,30,31]
    l=map(int,re.split("-|T|:|\n",time)[0:6])
    if l[2]>3:
        l[2]-=3
        return map(str,l)
    elif l[1]>1:
        l[1]-=1
        l[2]+=month[l[1]]-3
        if l[0]%4==0 and (l[0]%100 !=0 and l[0]%400==0):
            l[2]+=1
        return map(str,l)
    else:
        l[0]-=1
        l[1]=12
        l[2]+=28
        return map(str,l)

def handlePost(post):
    global count
    upTime,crTime=getTime(post)
    for p in post['data']:
        id=p['id']
    print "createTime: %s updateTime: %s id: %s" % (crTime,upTime,id)
    try:
        f=open(page+"/"+str(id),"r")
    except:
        f=open(page+"/"+str(id),"w")
        f.write('update time: 0')
        f.close()
        f=open(page+"/"+str(id),"r")
    uTime=f.readline()
    global T
    flag=False
    t0=time.clock()
    if re.split("-|T|:|\n",upTime)>re.split("-|T|:|\n",uTime[13:uTime.find('\n')]):
        flag=True    
    T=T+time.clock()-t0
    if flag:
        count+=1
        f=open(page+"/"+str(id),"w")
        f.write("update time: "+upTime+"\n")
        f.write("create time: "+crTime+"\n")
        f.write("id: "+id.encode("utf8")+"\n")
        dashline="----------------------------------------------------------------------------------------------------------\n"
        for p in post['data']:
            try:
                f.write("message:\n"+p['message'].encode("utf8")+"\n"+dashline)
            except:
                f.write("message:\n"+"\n"+dashline)
            try:
                f.write("like: "+str(p['like']['summary']['total_count'])+" ")
            except:
                f.write("like: 0 ")
            try:
                f.write("love: "+str(p['love']['summary']['total_count'])+" ")
            except:
                f.write("love: 0 ")
            try:
                f.write("haha: "+str(p['haha']['summary']['total_count'])+" ")
            except:
                f.write("haha: 0 ")
            try:
                f.write("wow:"+str(p['wow']['summary']['total_count'])+" ")
            except:
                f.write("wow: 0 ")
            try:
                f.write("sad: "+str(p['sad']['summary']['total_count'])+" ")
            except:
                f.write("sad: 0 ")
            try:
                f.write("angry: "+str(p['angry']['summary']['total_count'])+" \n"+dashline)
            except:
                f.write("angry: 0 ")
            try:
                for pp in p['comments']['data']:
                    f.write("created time: "+pp['created_time'].encode("utf8")+'\n')
                    f.write("id: "+pp['from']['id'].encode("utf8")+'\n')
                    f.write("name: "+pp['from']['name'].encode("utf8")+'\n')
                    f.write("comment: "+pp['message'].encode("utf8")+'\n'+dashline)
            except:
                f.write("")

        print "update finish"
    f.close()
    
    if "next" in post['paging']:
        handlePost(getData(post['paging']['next']))
    else:
        updateUntil(getSince())
        updateSince(getSince())

def mayUpdate(data):
    return "posts" in data

def setSince():
    global since
    if since!='':
        updateSince(until)
        f=open(page+"/realSince",'w')
        f.write(since)
    else:
        f=open(page+"/realSince",'r')
        since=f.readline()
    f.close()
def setUntil():
    global until
    if until!='':
        f=open(page+"/until",'w')
        f.write(until)
        ff=open(page+"/realUntil",'w')
        ff.write(until)
        ff.close()
    else:
        f=open(page+"/realUntil",'r')
        until=f.readline()
    f.close()
def main():
    global token,page,since,until
    token=raw_input("Please input token: ")
    page=raw_input("Please input page: ")
    since=raw_input("Please input since(eg:2017-11-01T00:00:00): ")
    until=raw_input("Please input until(eg:2017-11-03T00:00:00): ")
    setSince()
    setUntil()
    while True:
        data=getData(getUrl())
        print "Since: %s Until: %s" % (since,until)
        if mayUpdate(data):
            handlePost(data['posts'])
        else:
            updateUntil(getSince())
            updateSince(getSince())
        f=open(page+"/since",'r')
        if since==f.readline():
            f.close()
            break
        f.close()
        print 'Wating 10 seconds or press ctrl+c to exit'
        time.sleep(10)
    print "All Finish "
    print "Time for compare: %f s" % (T)
main()
