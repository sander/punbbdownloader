# This file is part of PunBBDownloader.
# Copyright (C) 2007  Sander Dijkhuis
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys,os,ConfigParser,urllib,punbbparser
from sys import exit

parser=punbbparser.PunBBHTMLParser()
loc='' # board location
tar='' # download target

def dl(src,target):
 urllib.urlretrieve(loc+src,tar+target)

if len(sys.argv)!=2:
 print 'Usage: python download.py /path/to/configuration/file'
 print '(So specify a configuration file to this command.)'
 print '(See the manual for instructions on how to create one.)'
 exit(2)

if not os.path.exists(sys.argv[1]):
 exit("The configuration file you specified doesn't seem to exist.")
if not os.access(sys.argv[1], os.R_OK):
 exit('Cannot read the configuration file. Check the permission settings.')

print 'Trying to check and read configuration file...'
cfg=ConfigParser.SafeConfigParser()
try:
 cfg.read(sys.argv[1])
except:
 exit('Could not parse the configuration file.')
try:
 locl=[v for k,v in cfg.items('Extern') if k=='location']
 if len(locl)==1:
  loc=locl[0]
 else:
  exit('No board location defined in the configuration file.')
 tarl=[v for k,v in cfg.items('LocalTargets') if k=='download']
 if len(tarl)==1:
  tar=tarl[0]
 else:
  exit('No download target defined in the configuration file.')
except ConfigParser.NoSectionError:
 exit('Not all required sections are available in the configuration file.')
if loc[-1:]!='/':
 exit('The board location URL should have a trailing slash (/).')
if tar[-1:]!='/':
 exit('The download target path should have a trailing slash (/).')
if not os.access(tar,os.W_OK):
 exit('Cannot write to the specified target location.')
if len(os.listdir(tar))!=0:
 exit("The target directory should be empty, but isn't.")
print '  Done.'

print 'Downloading and reading the board index...'
dl('index.php','index.html')
parser.open(tar+'index.html')
print '  Done.'

if parser.hasrulespage==True:
 print 'Downloading the rules...'
 dl('misc.php?action=rules','rules.html')
 print '  Done.'

topicids=[]

for fid in parser.forumids:
 print 'Downloading and reading the forum with ID %d...'%fid
 dl('viewforum.php?id=%d'%fid,'forum-%d.html'%fid)
 parser.open(tar+'forum-%d.html'%fid)
 for topic in parser.topicids:
  if topicids.count(topic)==0:
   topicids.append(topic)
 print '  Done.'
 for page in parser.pages:
  print 'Downloading and reading page %d of the forum with ID %d...'%(page,fid)
  dl('viewforum.php?id=%d&p=%d'%(fid,page),'forum-%d-p%d.html'%(fid,page))
  parser.open(tar+'forum-%d-p%d.html'%(fid,page))
  for topic in parser.topicids:
   if topicids.count(topic)==0:
    topicids.append(topic)
  print '  Done.'

for tid in topicids:
 print 'Downloading and reading the topic with ID %d...'%tid
 dl('viewtopic.php?id=%d'%tid,'topic-%d.html'%tid)
 parser.open(tar+'topic-%d.html'%tid)
 print '  Done.'
 for page in parser.pages:
  print 'Downloading and reading page %d of the topic with ID %d...'%(page,tid)
  dl('viewtopic.php?id=%d&p=%d'%(tid,page),'topic-%d-p%d.html'%(tid,page))
  print '  Done.'

print 'Downloading and reading the user list...'
dl('userlist.php','userlist.html')
parser.open(tar+'userlist.html')
userids=[]
for user in parser.userids:
 if userids.count(user)==0:
  userids.append(user)
print '  Done.'
for page in parser.pages:
 print 'Downloading and reading page %d of the user list...'%(page)
 dl('userlist.php?p=%d'%page,'userlist-p%d.html'%page)
 parser.open(tar+'userlist-p%d.html'%page)
 for user in parser.userids:
  if userids.count(user)==0:
   userids.append(user)
 print '  Done.'

for uid in userids:
 print 'Downloading the profile of user with ID %d...'%uid
 dl('profile.php?id=%d'%uid,'profile-%d.html'%uid)
 print '  Done.'

print "I've done what I had to do. You can run other PunBBDownloader scripts",\
 'now to make the downloaded pages usable.'
