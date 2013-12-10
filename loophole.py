# -*- coding: utf-8 -*-
##ALX {'tag':{'website','tornado','loophole'},'ver':'0','env':'python 2.7.3'}

import random
import re
import os
import sqlite3   
from time import localtime,mktime,strftime 
from datetime import datetime

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpserver
import tornado.log
from tornado import gen
from tornado.httpclient import AsyncHTTPClient

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class LoopholeHandler(tornado.web.RequestHandler):
	def __init__(self, application, request, **kwargs):
		super(LoopholeHandler, self).__init__(application, request, **kwargs)
		self.logger=self.application.logger

	def get_current_user(self):
		return self.get_secure_cookie('user')


class MainHandler(LoopholeHandler):
	def get(self):
		self.render('index.html')
 
class LoginHandler(LoopholeHandler):
	def get(self):
		username=self.get_current_user()
		if username: self.redirect('home')
		else: self.render('login.html')

	def post(self):
		try: next=self.get_argument('next')
		except: next='home'
		name=self.get_argument('txtUser')
		passwd=self.get_argument('txtPasswd')
		if self.checkuser(name,passwd):
			self.set_secure_cookie('user',name)
			self.logger.info('Login '+name)
			self.redirect(next)
		else:
			self.redirect(self.request.uri)

	def checkuser(self,name,passwd):
		with sqlite3.connect('data/user') as conn:
			cur=conn.cursor()
			if self.application.loophole_en:
				cur.execute('select name from tuser where name="'+name+'" and passwd="'+passwd+'";')
			else:
				cur.execute('select name from tuser where name=? and passwd=?;',(name,passwd))
			if cur.fetchone(): return True
			else: return False 

class AdminHandler(LoopholeHandler):
	@tornado.web.authenticated
	def get(self):
		self.render('admin.html',loophole_en=self.application.loophole_en)

	def post(self):
		frmid=self.get_argument('hidId')
		if frmid=='frm1':
			print 'frm1'
			passwd=self.get_argument('txtPasswd')
			with sqlite3.connect('data/user') as conn:
				cur=conn.cursor()
				cur.execute('update tuser set passwd=? where name="admin";',(passwd,))
				conn.commit()
		elif frmid=='frm2':
			print 'frm2'
			try:
				self.get_argument('chkLoophole')
				self.application.loophole_en=True
			except:
				self.application.loophole_en=False
		self.redirect('admin')
		
class LogoutHandler(LoopholeHandler):
	def get(self):
		self.clear_cookie('user')
		self.redirect('home')

class ResetHandler(LoopholeHandler):
	def get(self):
		self.set_secure_cookie('user','admin')
		self.redirect('admin')

class Loophole(tornado.web.Application):
	def __init__(self):     
		handlers=[
			(r'/home', MainHandler),
			(r'/login', LoginHandler),
			(r'/admin', AdminHandler),
			(r'/logout', LogoutHandler),
			(r'/single', ResetHandler),
		]
		settings = {
			'static_path': siteJoin('static'),
			'template_path': siteJoin('pages'), 
			'cookie_secret': 'dlasvjldsajvlkdjsaudksahvrnelzikchvleoqpeoihvfn',
			'login_url': '/login',
		}
		
		import logging
		self.logger=tornado.log.app_log
		if tornado.options.options.logging=='debug':
			settings['debug']=True
			self.logger.debug('Debug Mode')
			self.siteversion=str(datetime.now())
		else:
			self.siteversion=''

		tornado.web.Application.__init__(self, handlers, **settings)

		self.loophole_en=True


sitePth=os.path.dirname(__file__)
def siteJoin(rpth):
	return os.path.join(sitePth,rpth)

if __name__ == '__main__':
	tornado.options.define('port', default=8888, type=int)
	tornado.options.define('load_balancer', default='none', type=str)
	tornado.options.parse_config_file(siteJoin('server.conf'))

	dbs=['user']
	for dbi in dbs:
		if not os.path.exists('data/'+dbi) and os.path.exists('data/'+dbi+'.sql'):
			sqlsch=open('data/'+dbi+'.sql')
			with sqlite3.connect('data/'+dbi) as conn:
				conn.executescript(sqlsch.read())
				conn.commit()
			sqlsch.close()

	if tornado.options.options.load_balancer=='nginx':
		prototype = tornado.httpserver.HTTPServer(Loophole(),xheaders=True)
	else:
		prototype = tornado.httpserver.HTTPServer(Loophole())

	prototype.listen(tornado.options.options.port)
	tornado.ioloop.IOLoop.instance().start()
	