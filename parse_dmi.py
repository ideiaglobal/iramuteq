#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2014, Pierre Ratinaud
#License: GNU GPL

import csv, codecs, cStringIO
import itertools
from parse_factiva_xml import PrefImport
import wx
import os
from functions import BugReport

#filein = '/home/pierre/workspace/iramuteq/dev/dmi-tcat/travail_dmi.csv'
#fileout = '/home/pierre/workspace/iramuteq/dev/dmi-tcat/corpus.txt'

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class ParseDMI :
    def __init__(self, filein, fileout, encodeout ='utf8', onlyrt = True, cleanurl = True, cleanRT = True, cleanAt = True, lang= 'es'):
        self.outf = open(fileout, 'w')
        self.encodeout = encodeout
        with open(filein, 'rb') as f:
            reader = UnicodeReader(f)
            linenb = 0
            for row in reader:
                if linenb == 0 :
                    first = row
                    self.create_dateid = first.index('created_at')
                    textid = first.index('text')
                    langid = first.index('lang')
                else :
                    text = row[textid]
                    text = self.washtweet(text)
                    isrt = self.isRT(text)
                    if cleanurl :
                        text = self.cleanurl(text)
                    if cleanRT :
                        text = self.cleanRT(text)
                    if cleanAt :
                        text = self.cleanAt(text)
                    if onlyrt and not isrt :
                        if lang == 'all' :
                            self.write_tweet(row, text)
                        elif row[langid] == lang :
                            self.write_tweet(row, text)
                    if not onlyrt :
                        if lang == 'all' :
                            self.write_tweet(row, text)
                        elif row[langid] == lang :
                            self.write_tweet(row, text)
                linenb += 1
        self.outf.close()
    
    def write_tweet(self, row, text):
        meta = self.makemetadata(row, {'date' : self.create_dateid})
        self.outf.write('\n'.join([meta, text, '']).encode(self.encodeout))
    
    def makemetadata(self, row, parametres = {}):
        line = [u'****']
        for val in parametres :
            if val == 'date' :
                line.append('_'.join([u'*date', row[parametres[val]].split()[0]]))
            else :
                line.append('_'.join([val,row[parametres[val]]]))
        return ' '.join(line)
    
    def washtweet(self, text) :
        text = text.replace(u'RT“', u'RT ')
        text = text.replace(u'*', ' ')
        for val in u'”«»“"' :
            text = text.replace(val, ' " ')
        text.strip()
        return text

    def isRT(self, tweet):
        if tweet.startswith('RT ') :
            return True
        else :
            return False

    def cleanurl(self, tweet) :
        return ' '.join([word for word in tweet.split() if not word.startswith('http')])

    def cleanAt(self, tweet) :
        return ' '.join([word for word in tweet.split() if not word.startswith('@')])

    def cleanRT(self, text) :
        text = ''.join([' ',text, ' '])
        text.replace('rt','_rt_')
        text = text.replace('RT', '_rt_')
        text.strip()
        #tweet = text.split()
        #tovire = [[i, i+1] for i, word in enumerate(tweet) if word == 'RT' and i!=len(tweet) - 1]
        #tovire = itertools.chain(*tovire)
        #text = ' '.join([word for i, word in enumerate(tweet) if i not in tovire])
        return text

class ImportDMI :
    def __init__(self, parent, parametres):
        self.ira = parent
        self.parametres = parametres
        self.parse()
    
    def parse(self):
        self.dial =  PrefImport(self.ira, methode='dmi')
        val = self.dial.ShowModal()
        if val == wx.ID_OK :
            csvfile = self.dial.dbb.GetValue()
            corp_out = self.dial.fbb.GetValue()
            nort = self.dial.paneldmi.check_removeR_rt.GetValue()
            remove_url = self.dial.paneldmi.check_remove_url.GetValue()
            remove_mention = self.dial.paneldmi.check_remove_mention.GetValue()
            remove_rt_in_tweets = self.dial.paneldmi.check_remove_rt_in_tweets.GetValue()
            self.dial.Destroy()
            busy = wx.BusyInfo(_("Please wait...").decode('utf8'))
            wx.SafeYield()
            try :
                ParseDMI(csvfile, corp_out, 'utf8', onlyrt=nort, cleanurl=remove_url, cleanAt=remove_mention, cleanRT=remove_rt_in_tweets)
                del busy
                msg = '\n'.join([_(u"Corpus created :").decode('utf8'), corp_out, _(u"Do you want to open it in IRaMuTeQ ?").decode('utf8')])
                dlg = wx.MessageDialog(self.ira, msg, _(u'Information').decode('utf8'), wx.YES_NO | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
                dlg.CenterOnParent()
                val = dlg.ShowModal()
                if val == wx.ID_YES :
                    dlg.Destroy()
                    self.ira.filename = os.path.abspath(corp_out)
                    self.ira.OpenText()
                else :
                    dlg.Destroy()
            except :
                del busy
                BugReport(self.ira)
        else :
            self.dial.Destroy()       
        
#ParseDMI(filein, fileout, 'utf8')