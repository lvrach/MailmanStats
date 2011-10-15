#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import mailbox, sys, re, pyratemp, time
from os import path, walk, mkdir
import argparse
from pychart import *

### GLOBAL ###
# Constants
MONTH = "(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
YEAR = "(?P<year>[0-9]{2,4})"
DAY = "(Mon|Tue|Wed|Thu|Fri|Sat|Sun)"
TIME = "(?P<time>[0-9:]{8})"
DATE = "(?P<date>[0-9]{1,2})"
MAILPROG = re.compile("([A-Za-z0-9._%+-]+)[@]([A-Za-z0-9.-]+)[.]([A-Za-z]{2,4})")
DATEREGEX = (DAY+"[,][ ]"+DATE+"[ ]"+MONTH+"[ ]"+YEAR+"[ ]"+TIME, DAY+"[ ]"+MONTH+"[ ]"+DATE+"[ ]"+TIME+"[ ]"+YEAR, DATE+"[ ]"+MONTH+"[ ]"+YEAR+"[ ]"+TIME,
DATEPROG = [re.compile(d) for d in DATEREGEX]


# Functions
def plotBarGraph(data, outputfile, xlabel, ylabel, thumb = False, limitable = False):
    cropped = []
    theme.output_format = "png"
    theme.output_file = outputfile
    theme.scale_factor = 1.5
    theme.use_color = True
    theme.reinitialize()

    if len(data) > limit and limitable:
        data = data[:limit]

    for d in data:
        if len(d[0]) > 21:
            cropped.append([d[0][:21]+"...", d[1]])
        else:
            cropped.append([d[0], d[1]])

    fs = fill_style.Plain(bgcolor=color.lightblue)
    if not thumb:
        yaxis = axis.Y(label="/b/15"+ylabel, format = "%d")
        xaxis = axis.X(format=lambda x: "/a80/H"+x, label = "/b/15"+xlabel, tic_label_offset = (-3,0))
        ar = area.T(size = (12*len(data)+50,400), x_coord = category_coord.T(cropped, 0), x_axis = xaxis, y_axis = yaxis, y_range = (0,None), legend = None)
        ar.add_plot(bar_plot.T(data = cropped, fill_style = fs, data_label_format="/a75{}%d", data_label_offset=(3,10)))
    else:
        ar = area.T(size = (250,150), x_coord = category_coord.T(cropped, 0), y_range = (0,None), legend = None)
        ar.add_plot(bar_plot.T(data = cropped, fill_style = fs))
    ar.draw()

def getMlName(mboxpath):
    dot = path.basename(mboxpath).find(".")
    return path.basename(mboxpath)[:dot]


def dictSub(text, dictionary):
    prog = re.compile('|'.join(map(re.escape, dictionary)))
    return prog.sub(str(dictionary[prog.match(text).group(0)]), text)


def monthlySort(data):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "Octomber", "November", "December"]
    firstyear = int(min(data.keys())[:4])
    lastyear = int(max(data.keys())[:4])
    firstmonth = int(min(data.keys())[-2:])
    r = ""
    y = firstyear
    m = firstmonth
    years = {}

    while r != max(data.keys()):
        m += 1
        if m % 12 == 1:
            m = 1
            y += 1
        r = "%i%02d" % (y,m)
        if r not in data:
            data[r] = 0

    for year in range(firstyear, lastyear+1):
        peryear = [[months[int(yearmonth[-2:])-1], data[yearmonth]] for yearmonth in data.keys() if int(yearmonth[:4]) == year]
        years[year] = sorted(peryear, key=lambda x: months.index(x[0]))
    return (years, firstyear, lastyear+1)


# Dictionary of Authors
class Authors:
    def __init__(self):
        self.authors = {}
        self.sorted_authors_emails = []
        self.sorted_authors_threads = []
        self.totalmails = 0                                                                                                                                                                                
        self.totalthreads = 0
        self.totalmonth = {}
        self.years = []
        self.yearmsg = {}

    def parseMsg(self, msg):
        if (msg.from_mail not in self.authors):
            author = Author(msg.from_mail, msg.date)
            self.authors[msg.from_mail] = author
            self.totalmails += 1
        else:
            self.totalmails += 1
            self.authors[msg.from_mail].posts += 1
            self.authors[msg.from_mail].lastmsgdate = msg.date
            self.authors[msg.from_mail].lastmsgdatestr= time.ctime(msg.date)

        try:
            if "Re:" not in msg.subject or not msg.subject:
                self.authors[msg.from_mail].started += 1
                self.totalthreads += 1
        except TypeError:
            pass
        
        if msg.month[:4] not in self.yearmsg:
            self.yearmsg[msg.month[:4]] = 1
        else:
            self.yearmsg[msg.month[:4]] += 1

        if msg.month not in self.totalmonth: self.totalmonth[msg.month] = 1
        if msg.month not in self.authors[msg.from_mail].monthdic: self.authors[msg.from_mail].monthdic[msg.month] = 1
        else: 
            self.authors[msg.from_mail].monthdic[msg.month] += 1
            self.totalmonth[msg.month] += 1

    def calcAverage(self):
        for a in self.authors:
            try: self.authors[a].average = str(round(self.authors[a].posts / int((time.time() - self.authors[a].firstmsgdate) / 86400), 3))
            except ZeroDivisionError: pass

    def calcStats(self):
        self.calcAverage()
        self.sortAuthors()
        self.createUserPages()
        self.plotEmailsPerAuthor()
        self.plotThreadsPerAuthor()
        self.plotMonthlyUsage()
        self.plotYearlyUsage()
    
    def sortAuthors(self):
        self.sorted_authors_emails = sorted(self.authors, key=lambda x:self.authors[x].posts, reverse=True)
        self.sorted_authors_threads = sorted(self.authors, key=lambda x:self.authors[x].started, reverse=True)

    def createUserPages(self):
        for a in self.authors:
            peryear, fy, ly = monthlySort(self.authors[a].monthdic)
            for year in xrange(fy, ly):
                self.authors[a].years.append(year)
                plotBarGraph(peryear[year], outputdir+"/ml-files/ml-"+self.authors[a].pagename+"-usage-"+str(year)+".png", "Months", "Emails")
            f = open(outputdir+"/ml-files/ml-"+self.authors[a].pagename+".html", 'w')
            t = pyratemp.Template(filename='user.tpl')
            result = t(heading=mlname, author=self.authors[a], encoding="utf-8")
            f.write(result)

    def plotEmailsPerAuthor(self):
        tmp = [[a, self.authors[a].posts] for a in self.sorted_authors_emails]
        plotBarGraph(tmp, outputdir+"/ml-files/ml-emailsperauthor.png", "Authors", "Emails", limitable = True)
        plotBarGraph(tmp, outputdir+"/ml-files/ml-emailsperauthor-thumb.png", "Authors", "Emails", thumb = True, limitable = True)

    def plotThreadsPerAuthor(self):
        tmp = [[a, self.authors[a].started] for a in self.sorted_authors_threads]
        plotBarGraph(tmp, outputdir+"/ml-files/ml-threadsperauthor.png", "Authors", "Threads", limitable = True)
        plotBarGraph(tmp, outputdir+"/ml-files/ml-threadsperauthor-thumb.png", "Authors", "Threads", thumb = True, limitable = True)

    def plotYearlyUsage(self):
        tmp = [[a, self.yearmsg[a]] for a in self.yearmsg]
        tmp = sorted(tmp, key=lambda x: x[0])
        plotBarGraph(tmp, outputdir+"/ml-files/ml-yearlyusage.png", "Years", "Emails")
        plotBarGraph(tmp, outputdir+"/ml-files/ml-yearlyusage-thumb.png", "Years", "Emails", thumb = True)

    def plotMonthlyUsage(self):
        peryear, fy, ly = monthlySort(self.totalmonth)
        for year in xrange(fy, ly):
            self.years.append(year)
            plotBarGraph(peryear[year], outputdir+"/ml-files/ml-usage-"+str(year)+".png", "Months", "Emails")


    def __str__(self):
        for author in self.authors:
            print(self.authors[author])

# Represents the author of the post probably a subscriber of the list
class Author:
    def __init__(self, mail, date):
        if options.masked: self.mail = self.maskMail(mail)
        else: self.mail = mail
        self.posts = 1
        self.started = 0
        self.lastmsgdate = date
        self.lastmsgdatestr = time.ctime(date)
        self.firstmsgdate = date
        self.firstmsgdatestr = time.ctime(date) 
        self.name = self.getName(self.mail)
        self.pagename = self.getPagename(self.mail)
        self.monthdic = {}
        self.years = []
        self.average = 0

    def maskMail(self, mail):
        r = MAILPROG.match(mail) #FIXME
        cut = int((len(r.group(1))-2) /2)
        name = r.group(1)[:-cut]
        middle = r.group(2)[0]+"..."+r.group(2)[-1]
        mail = name +"...@"+  middle + "." +  r.group(3)
        return mail

    def getPagename(self, mail):
        mail = mail.replace('@', 'at')
        return  mail

    def getName(self, mail):
        at = mail.find('@')
        return mail[:at]

    def __str__(self):
        return self.mail+" "+str(self.posts)+" "+str(self.started)+" "+str(self.lastmsgdate)

class Message:
    def __init__(self, message):
        self.subject = message['subject']
        r = MAILPROG.search(message['from'])
        if not r:
            raise TypeError #FIXME
        self.from_mail = r.group(0)
        for d in DATEPROG:
            r = d.search(message['date']) #FIXME
            print message['date']
            if r:
                print "mpika"
                if len(r.group('year')) == 4:
                    t = time.strptime(r.group('date')+" "+r.group('month')+" "+r.group('year')+" "+r.group('time'), '%d %b %Y %H:%M:%S')
                else:
                    t = time.strptime(r.group('date')+" "+r.group('month')+" "+r.group('year')+" "+r.group('time'), '%d %b %y %H:%M:%S')
                print time.mktime(t)
                self.date = time.mktime(t)
                self.month = r.group('month')
                break

    def getMonth(self, date):
        r = MONTHPROG.search(date) #FIXME
        months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        month = dictSub(r.group(1), months)
        return "%s%02d" % (r.group(2), int(month))


    def __str__(self):
        print self.subject+" "+self.from_mail+" "+self.date
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MailmanStats is a python script that generates an HTML report for a Mailman based mailing list. It takes the mailbox path as an argument and presents useful information such as mails sent per user, threads created per user, mails sent per month, activity per user and more. It also creates statistics and submits them using graphs.") # FIXME add epilog
    parser.add_argument("-o", "--output", default="./", dest="output", help="Use this option to change the output directory. Default: Current working directory.")
    parser.add_argument("-l", "--limit", type=int, default=100, dest="limit", help="Choose the number of authors you want to be shown in the charts. Default top 100 authors.")
    parser.add_argument("-u", "--unmask", default=True, dest="masked", action="store_false", help="Use this option to show email addresses.")
    parser.add_argument("-d", "--debug", default=False, dest="debug", action="store_true", help="Use this option if you want to enable debug output.")
    parser.add_argument("mbox", help="Mbox File")
    options = parser.parse_args()

    if not path.isfile(options.mbox):
        print "This is not a file!"
        sys.exit()

    mbox = mailbox.mbox(options.mbox)
    outputfile = "ml-report.html"
    limit = options.limit
    outputdir = options.output
    authors = Authors()
    mlname = getMlName(options.mbox)
    dbg = options.debug

    # Create Directory for extra files
    try:
        mkdir(outputdir+"/ml-files/")
    except OSError, e:
        if dbg:
            print e # FIXME

    # Parse all messages in mbox file
    for message in mbox:
        try:
            msg = Message(message)
            authors.parseMsg(msg)
        except TypeError, e:
            if dbg:
                print e #FIXME
            continue

    authors.calcStats()

    #  Generate ml-report.html
    f = open(outputfile, 'w')
    t = pyratemp.Template(filename='report.tpl')
    result = t(heading=mlname, totalmails=authors.totalmails, totalthreads=authors.totalthreads, mydic=authors.authors, sa=authors.sorted_authors_emails, yr=authors.years, ac=len(authors.authors))
    f.write(result)
    f.close()



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
