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

# This script isn't finished. You could try to use it, it worked for me, but you
# could also wait until it's finished.
# -Sander

import sys,os,ConfigParser,tidy,re
from sys import exit

loc='' # board location
dlt='' # download target
out='' # output target

if len(sys.argv)!=2:
 print 'Usage: python makearchive.py /path/to/configuration/file'
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
 dltl=[v for k,v in cfg.items('LocalTargets') if k=='download']
 if len(dltl)==1:
  dlt=dltl[0]
 else:
  exit('No download target defined in the configuration file.')
 outl=[v for k,v in cfg.items('LocalTargets') if k=='output']
 if len(outl)==1:
  out=outl[0]
 else:
  exit('No output target defined in the configuration file.')
except ConfigParser.NoSectionError:
 exit('Not all required sections are available in the configuration file.')
if loc[-1:]!='/':
 exit('The board location URL should have a trailing slash (/).')
if dlt[-1:]!='/':
 exit('The download target path should have a trailing slash (/).')
if out[-1:]!='/':
 exit('The output target path should have a trailing slash (/).')
if not os.access(out,os.W_OK):
 exit('Cannot write to the specified output location.')
if len(os.listdir(out))!=0:
 exit("The output directory should be empty, but isn't.")
print '  Done.'

print 'Getting a list of files that should be processed...'
files=os.listdir(dlt)
print '  Done.'

links={'index.php':'index.html','misc.php?action=rules':'rules.html',
 'userlist.php':'userlist.html'}
print 'Getting new locations for pages...'
for file in files:
 if file[:8]=='userlist' and not file=='userlist.html':
  links['userlist.php?username=&show_group=-1&sort_by=username&sort_dir=ASC&p='
   +file.split('-p')[1].split('.')[0]]=file
 elif file[:5]=='forum':
  split=file[6:][:-5].split('-p')
  if len(split)==1:
   links['viewforum.php?id='+split[0]]=file
   split.append('1')
  links['viewforum.php?id=%s&p=%s'%(split[0],split[1])]=file
 elif file[:5]=='topic':
  split=file[6:][:-5].split('-p')
  if len(split)==1:
   links['viewtopic.php?id='+split[0]]=file
   split.append('1')
  links['viewtopic.php?id=%s&p=%s'%(split[0],split[1])]=file
  f=open(dlt+file,'r')
  s=f.read()
  f.close()
  posts=re.compile('<div id="p([0-9]+)"').findall(s)
  for post in posts:
   links['viewtopic.php?pid='+post]=file
 elif file[:7]=='profile':
  links['profile.php?id=%s'%file[8:][:-5]]=file
nlinks={}
for old,new in links.iteritems():
 old=old.replace('&','&amp;')
 nlinks[old]=new
# nlinks[loc+old]=new
links=nlinks
print '  Done.'

for file in files:
 print 'Processing %s (file %d of %d)...'%(file,files.index(file)+1,len(files))
 f=open(dlt+file,'r')
 s=f.read()
 f.close()
 s=s.replace('&nbsp;&raquo;&nbsp;','&raquo; ')
 s=s.replace(' </a>&nbsp;</li>','</a></li>')
 options=dict(output_xhtml=1,
             add_xml_space=1,
             input_encoding='latin1',
             output_encoding='utf8',
             tidy_mark=0,
             wrap=0,
             quote_nbsp=1)
 s=str(tidy.parseString(s,**options))
 # remove mypunbb's ads
 s=re.compile('<div style="TEXT-ALIGN.*?<br />',re.DOTALL).sub('',s)
 s=re.compile('<li id="(navsearch|navregister|navlogin)">.*?</li>').sub('',s)
 s=re.compile('<div class="postfoot(left|right)">.*?</div>',re.DOTALL).sub('',s)
 s=re.compile('<div id="brdwelcome".*?</div>',re.DOTALL).sub('',s)
 s=re.compile('<div class="conl">\n<form.*?</form>\n</div>',re.DOTALL).sub('',s)
 s=re.compile('Hosted by.*?<br />').sub('',s)
 s=s.replace('Andersson</p>\n<div class="clearer">','Andersson<br />\nArchived'\
  +' by <a href="http://code.google.com/p/punbbdownloader/">PunBBDownloader</a'\
  +'></p>\n<div class="clearer">')
 s=re.compile('<p class="postlink conr">.*?</p>').sub('',s)
 s=re.compile('- <a href="search\.php\?action=show_user.*?</dd>',re.DOTALL
  ).sub('',s)
 s=re.compile('<div class="blockform">.*?</div>\n</div>',re.DOTALL).sub('',s)
 s=re.compile('<dl id="searchlinks".*?</dl>',re.DOTALL).sub('',s)
 s=re.compile('<dl class="conl">.*?</dl>',re.DOTALL).sub('',s)
 #tmp
 s=s.replace('<link rel="stylesheet" type="text/css" href="style/Oxygen.css" />','<link rel="stylesheet" type="text/css" href="Oxygen.css" />')
 s=s.replace('<img src="img/smilies/','<img src="smiley-')
 n=1
 for old,new in links.iteritems():
  #s=re.compile('<a href="[%s]?%s(#|")'%(loc,old)).sub(r'<a href="%s\1'%new,s)
  s=s.replace('<a href="%s">'%old,'<a href="%s">'%new)
  s=s.replace('<a href="%s#'%old,'<a href="%s#'%new)
  s=s.replace('<a href="%s%s">'%(loc,old),'<a href="%s">'%new)
  s=s.replace('<a href="%s%s#'%(loc,old),'<a href="%s#'%new)
  print n
  n+=1
  # a faster solution might be one regexp, that also takes care of adding loc
 # tidy things up again and save it
 #options['indent']='auto'
 options['input_encoding']='utf8'
 options['wrap']=80
 s=str(tidy.parseString(s,**options))
 s=s.replace('&nbsp;','&#160;')
 f=open(out+file,'w')
 f.write(s)
 f.close()
 print '  Done.'
