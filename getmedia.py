# This file is part of PunBBDownloader.
# Copyright (C) 2010  Sander Dijkhuis
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

import ConfigParser
import os
import re
import sys
import urllib

location = ''
dltarget = ''
target = ''

def download(src, name):
    urllib.urlretrieve(location + src, target + name)

if len(sys.argv) != 2:
    print 'Usage: python getmedia.py /path/to/configuration/file'
    print '(See the manual for details.)'

print 'Trying to check and read configuration file...'
cfg = ConfigParser.SafeConfigParser()
try:
    cfg.read(sys.argv[1])
except:
    exit('Could not parse the configuration file.')
try:
    locl = [v for k, v in cfg.items('Extern') if k == 'location']
    if len(locl) == 1:
        location = locl[0]
    else:
        exit('No board location defined in the configuration file.')
    dll = [v for k, v in cfg.items('LocalTargets') if k == 'download']
    if len(dll) == 1:
        dltarget = dll[0]
    else:
        exit('No download location defined in the configuration file.')
    tarl = [v for k, v in cfg.items('LocalTargets') if k == 'media']
    if len(tarl) == 1:
        target = tarl[0]
    else:
        exit('No media download target defined in the configuration file.')
except ConfigParser.NoSectionError:
    exit('Not all required sections are available in the configuration file.')
if location[-1:] != '/':
    exit('The board location URL should have a trailing slash (/).')
if target[-1:] != '/':
    exit('The media download target path should have a trailing slash (/).')
if not os.access(target, os.W_OK):
    exit('Cannot write to the specified media download target location.')
if len(os.listdir(target)) != 0:
    exit("The media download target directory should be empty, but isn't.")
print '  Done.'

print 'Downloading style sheets...'
download('style/Oxygen.css', 'Oxygen.css')
download('style/imports/base.css', 'base.css')
download('style/imports/Oxygen_cs.css', 'Oxygen_cs.css')
print '  Done.'

print 'Changing import URLs in main style sheet...'
f = open(target + 'Oxygen.css', 'r')
s = f.read()
f.close()
s = s.replace('imports/', '')
f = open(target + 'Oxygen.css', 'w')
f.write(s)
f.close()
print '  Done.'

print 'Downloading smilies...'
smilies = ['big_smile', 'cool', 'hmm', 'lol', 'mad', 'neutral', 'roll', 'sad', 'smile', 'tongue', 'wink', 'yikes']
for name in smilies:
    download('img/smilies/%s.png' % name, 'smiley-%s.png' % name)
print '  Done.'

print 'Getting avatar locations...'
avatars = []
files = os.listdir(dltarget)
for name in files:
    if name[:8] != 'profile-':
        continue
    f = open(dltarget + name, 'r')
    s = f.read()
    f.close()
    found = re.compile('<img src="img/avatars/([^"]*)"').search(s)
    if found:
        avatars.append(found.group(1))
print '  Done.'

print 'Downloading avatars...'
for avatar in avatars:
    download('img/avatars/%s' % avatar, 'avatar-%s' % avatar)
print '  Done.'

print
print "That's all folks!"
