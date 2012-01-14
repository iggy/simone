"""IMAP4 client library

hopefully more pythonic than the original

TODO

folder->subfolders

"""

# Author: Brian Jackson <iggy@theiggy.com>


import binascii, os, random, re, socket, sys, time, email
from pprint import pprint

try:
	import simplejson
	class IMAP4FolderJSONEncoder(simplejson.JSONEncoder):
		"""a class to return a serialized version of an IMAP4Folder since it's
		basically just a list of messages

		This is probably specific to django-webmail (or some form of webmail
		anyways)

		USE:
		simplejson.dumps(IMAP4[folder], cls=imaplib2.IMAP4FolderJSONEncoder)
		"""
		def default(self, o):
			#o.debug('line 30', o)
			d = []
			[d.append(m) for m in o[0:6]]
			#o.debug(d)
			return d #[d.append(m) for m in self[0:]]

except:
	pass

IMAP4_PORT = 143
IMAP4_SSL_PORT = 993

class IMAP4Folder:
	def __init__(self, parent, name):
		self.parent = parent
		self.name = name

	def search(self):
		# TODO
		"""Search the folder"""
		pass

	def debug(self, *args):
		self.parent.debug(*args)

	def parseflags(self, flags):
		ret = []
		for x in flags.split(' '):
			ret.append(x)

		#self.debug('flags = ', ret)
		return ret

	def getflags(self, msgs):
		if ':' in msgs:
			ret = self.parent.docommand('FETCH %s (UID FLAGS)' % (msgs))
			d = {}
			for i in re.findall(r'\(UID (\d+) FLAGS \(([^\)]+)\)\)',  ret):
				d[i[0]] = i[1]
			return d
		else:
			ret = self.parent.docommand('FETCH %s:%s (UID FLAGS)' % (msgs, msgs))

	def addflag(self, uid, flag):
		self.parent.docommand('UID STORE %s:%s +FLAGS (%s)' % (uid, uid, flag))

	def delflag(self, uid, flag):
		self.parent.docommand('UID STORE %s:%s -FLAGS (%s)' % (uid, uid, flag))

	def setflags(self, msgs, flags):
		if ':' in msgs:
			# we probably have an imap list of msgs
			if isinstance(flags, dict):
				for u, f in flags.iteritems():
					self.parent.docommand('UID STORE %s:%s FLAGS (%s)' % (u, u, f))
			else:
				ret = self.parent.docommand('UID STORE %s FLAGS (%s)' % (msgs, ' '.join(flags)))
		else:
			f = ''
			for flag in flags:
				f += r'%s ' % (flag)
			self.parent.docommand('UID STORE %s:%s FLAGS (%s)' % (msgs, msgs, ' '.join(flags)))

	def __getitem__(self, key):
		if len(self) is 0:
			return []

		if isinstance(key, slice):
			lst = []

			(start, stop, stride) = key.indices(len(self))
			self.debug(start, stop, stride)
			if stride not in (None,1):
				self.debug('stride syntax for slices not supported')
				raise TypeError

			saveflags = self.getflags('%s:%s' % (start, stop))

			ret = self.parent.docommand('FETCH %s:%s (UID FLAGS INTERNALDATE RFC822)' % (start, stop))
			self.debug('fetch command ret = ',  ret)

			# the returned string looks something like this:
			# '* 1 FETCH (UID 1 FLAGS (\\Seen) INTERNALDATE "29-Jan-2007 10:25:56 -0600" RFC822 {1493}\r\nDelivered-To: dn.......<rest of the body>.....)\r\n'
			# OR (for a single message)
			# * 1 FETCH (UID 1 FLAGS (\\Seen $NotJunk) INTERNALDATE "07-Jan-2003 22:11:34 -0600" RFC822 {4453}\r\nReceived:...
			x = r'(?:\*|) \d+ FETCH \(UID (?P<uid>\d+) FLAGS \((?P<flagstr>[^)]+)\) '
			x += r'INTERNALDATE "(?P<imapdate>[^"]+)" '
			x += r'RFC822 {(?P<msgsize>\d+)}\r\n(?P<rfc822>[\s\S]+?)(?:\)\r\n$|\)\r\n\*|$)'

			r = re.findall(x, ret)

			for m in r:
				lst.append({
					'uid': m[0],
					'flags': self.parseflags(saveflags[m[0]]),
					'date':m[2],
					'size': m[3],
					'email': email.message_from_string(m[4]),
				})

			# need to reset the msg flags to what they originally were
			self.setflags('%s:%s' % (start, stop),  saveflags)
			for m in lst:
				self.setflags(m['uid'],  m['flags'])

			return lst

		elif isinstance(key, int):
			# we are going to assume they are looking for a uid
			pass

		return None

	def __len__(self):
		try:
			return self.folderlength
		except:
			ret = self.parent.docommand('SELECT %s' % (self.name))
			#self.debug('__len__ docommand return =',  ret,  'folder = %s' % (self.name))
			search = re.search('\* (?P<len>\d+) EXISTS', ret)
			#self.debug('__len__ search =', search.groups(),  search.group('len'))

			self.folderlength = int(search.group('len'))
			return self.folderlength


class IMAP4:
	"""A class for accessing IMAP4 servers

	The goal of this class is to be more pythonic than the imaplib that comes
	with python.

	That class is basically just a way to talk to an imap server. You still
	have to know what to say.

	With this class, the class instance represents a server. It has folders
	and subfolders, etc. The folders have email messages

	I'm mainly writing this class with django-webmail in mind, but hopefully it
	will be generally useful.
	"""

	class error(Exception): pass

#     class folders():
#         def __init__(self):
# 	    dir(self)
#
#         def showself(self):
# 	    pprint(self)

	def __init__(self, host = '', username = '', password = '', port = IMAP4_PORT):
		self.host = host
		self.username = username
		self.password = password
		self.port = port
		self.index = 0

		self.foldersep = "."
		self.foldercache = {}

		self.ident = 000001 # if you change this, you have to change the string slice indices in docommand

		self.gotfinish = True
		self.DEBUG = True

		# initialize the connection to the server and login
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((host, port))
		#self.sock.setblocking(0)
		self.file = self.sock.makefile('rb')
		connstr = self.file.readline()

		# capabilities
		self.caps = self.parsecaps(self.docommand('CAPABILITY'))
		self.debug(self.caps)
		#self.sock.sendall('001 CAPABILITY\r\n')
		#self.caps = self.parsecaps(self.file.readline())
		#if 'OK' not in self.readline():
			#raise self.error('CAPABILITY failed')

		self.auth()

		#self.folders = {}


	def auth(self):
		# FIXME support more auth mechanisms
		if 'CRAM-MD5s' in self.caps['authsupp']:
			import hmac
			password = hmac.HMAC(self.password, digest).hexdigest()
			#digest = self.docommand('AUTHENTICATE CRAM-MD5')
			digest = 'foo'
		else:
			import base64
			authstr = '\0%s\0%s\0' % (self.username, self.password)
			#self.docommand(authstr.b64encode())
			self.docommand('AUTHENTICATE PLAIN %s' % (base64.b64encode(authstr)))
			#sys.sleep(1)
			#self.sock.sendall('002 AUTHENTICATE %s %s\r\n' % (self.username, self.password))
			#self.file.readline()
			#if 'OK' not in self.file.readline():
				#raise self.error('LOGIN failed')

	def list_folders(self):
		try:
			return self.folderlist
		except:
			#self.sock.sendall('003 LIST "" *\r\n')
			resp = self.docommand('LIST "" *')
			self.debug('resp =',  resp )
			self.folderlist = re.findall(r'LIST \(.*\) "([^"]+)" "([^"]+)"', resp)
			#self.folderlist = re.findall(r'LIST .*', resp,  re.M)
			self.foldersep = self.folderlist[0][0]
			self.debug(self.foldersep)
			self.folderlist.sort()
			self.folderlist = [y for x, y in self.folderlist]
			#sorted = self.folderlist
			self.debug(self.folderlist)

			return self.folderlist

	def parsecaps(self, caps):
		#print caps
		c = {}

		try:
			c['ver'] = re.search(r'IMAP4[\w]+', caps, re.I).group()
		except:
			c['ver'] = None
		c['authsupp'] = re.findall(r'AUTH=([\w-]+)', caps)
		#c['namespace'] = re.search(r'NAMESPACE', caps).group()
		c['namespace'] = 'NAMESPACE' in caps


		#pprint(c)
		return c

	def docommand(self, command):
		# FIXME This thing still doesn't act right with out of order msgs, etc.
		# see how the other imaplib does it

		# read off anything the server may have sent us since our last command
		ret = ''
		self.sock.setblocking(0)
		while 1:
			try:
				ret += self.file.readline()
			except:
				break

		if ret != '':
			self.debug('server sent unexpected messages: ',  ret)
		self.sock.setblocking(1)

		ret = ''

		identstr = 'P%06d' % (self.ident)
		fullcmd = '%s %s\r\n' % (identstr, command)
		self.debug( fullcmd )

		self.sock.sendall(fullcmd)

		self.gotfinish = False
		while 1:
			line = self.file.readline()
			#self.debug( 'line: ',  line[:-2], line[0:7], identstr, line[8:10] )
			#print line[8:10]
			if line[0:7] == identstr:
				#self.debug('got ident string back')
				if line[8:10] in ['OK', 'NO']:
					#self.debug('OK or NO response')
					self.gotfinish = True
					break
				if line[8:11] is 'BAD' or line[2:5] is 'BAD':
					raise self.error('BAD response from server (%s)' % (line))
			if line == '' and self.gotfinish:
				self.debug('blank line returned')
				break

			ret = ret + line

		self.ident = self.ident + 1

		return ret

	def debug(self, *args):
		if not self.DEBUG:
			return

#		if len(args) == 1 and isinstance(args[0], str):
#			print ">>>>>>  %s  <<<<<<" % (args[0])
#			return

		print ">>>>>>"
		for d in args:
			pprint(d)
		print "<<<<<<"

	### couple of functions to get the magic folder access, etc. to work
	def __getitem__(self, key):
		try:
			self.folderlist
		except:
			self.list_folders()

		if key in self.folderlist:
			#self.debug('name =',  key)
			try:
				#self.debug('returning from cache: ',  self.foldercache[key])
				return self.foldercache[key]
			except:
				#self.debug('folder not in cache')
				self.foldercache[key] = IMAP4Folder(self, key)
				return self.foldercache[key]

#	def next(self):
#		self.index = self.index + 1
#		return IMAP4Folder(self, folderlist[self.index])


