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

from sgmllib import SGMLParser

class PunBBHTMLParser(SGMLParser):
 def open(self,file):
  self.reset()
  f=open(file,'r')
  self.feed(f.read())
  f.close()

 def reset(self):
  SGMLParser.reset(self)
  self.forumids=[]
  self.pages=[]
  self.blockclasses=[]
  self.blockids=[]
  self.topicids=[]
  self.userids=[]
  self.hasrulespage=False

 def start_a(self,attrs):
  href=[v for k,v in attrs if k=='href']
  if href:
   url=href[0].replace('&amp;','&')

   if url=='misc.php?action=rules':
    self.hasrulespage=True

   urlsplit=url.split('?id=')
   if urlsplit[0] in ['viewforum.php','viewtopic.php']:
    # urlsplit is probably something like ['viewforum.php', '123']
    inttest=None
    try:
     int(urlsplit[1])
     inttest=True
    except ValueError:
     # there are more GET things in the URL, so it probably isn't what we want
     inttest=False
    if inttest==True:
     if urlsplit[0]=='viewforum.php' and not urlsplit[1] in self.forumids:
      self.forumids.append(int(urlsplit[1]))
     if urlsplit[0]=='viewtopic.php' and not urlsplit[1] in self.topicids:
      self.topicids.append(int(urlsplit[1]))

   if (self.blockclasses.count('pagelink conl')==1 \
    or self.blockclasses.count('pagelink')==1) \
    and self.blockclasses.count('linkst')==1:
    # this anchor links to another page of this section
    urlsplit=url.split('&p=')
    if len(urlsplit)==2:
     if len(self.pages)==0:
      self.pages.append(int(urlsplit[1]))
     else:
      if int(urlsplit[1])>self.pages[-1]:
       self.pages=range(2,int(urlsplit[1])+1)

   if self.blockids.count('users1')==1:
    urlsplit=url.split('?id=')
    self.userids.append(int(urlsplit[1]))

 def start_div(self,attrs):
  cl=[v for k,v in attrs if k=='class']
  if cl:
   self.blockclasses.append(cl[0])
  else:
   self.blockclasses.append('')
  id=[v for k,v in attrs if k=='id']
  if id:
   self.blockids.append(id[0])
  else:
   self.blockids.append('')
  
 def end_div(self):
  self.blockclasses.pop()
  self.blockids.pop()

 start_p=start_div
 end_p=end_div
