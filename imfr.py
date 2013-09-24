import cherrypy
from mako.template import Template
#import sqlite3 as sqlite
from pysqlite2 import dbapi2 as sqlite
from math import sqrt
import demjson
from datetime import datetime
import time
import md5
from currency import convert

def isUsernameValid(con, username):
	cursor = con.cursor()
	query = "SELECT count(*) FROM USERS WHERE username=?"
	res = cursor.execute(query, (username, ))
	n = int(res.fetchone()[0])
	if n == 1:
		return True
	else:
		return False
	

class IMFR:
	
	@cherrypy.expose
	def default(self, username=None):
	
		con = sqlite.connect('imfr.db')
		if not con:
			return "no connection to DB"
			
		# the username was specified
		if username:
				
			if not isUsernameValid(con, username):
				pass
			else:
				cursor = con.cursor()
				# load currencies
				query = "SELECT code, name FROM CURRENCIES ORDER BY name ASC"
				res = cursor.execute(query)
				currencies = []
				for row in res.fetchall():
					currencies.append({'code': row[0], 'name': row[1]})
				# load profile details
				query = "SELECT username, default_currency FROM USERS WHERE username=?"
				res = cursor.execute(query, (username, ))
				row = cursor.fetchone()
				default_currency = row[1]
				# load the perso page
				template = Template(filename='perso.html', output_encoding='utf-8', encoding_errors='replace')
				page = template.render(
					username=username,
					currencies = currencies,
					default_currency = default_currency)
				con.close()
				return page
			
		# no (or no valid) username specified: return the homepage
		cursor = con.cursor()
		query = "SELECT code, name FROM CURRENCIES ORDER BY name ASC"
		res = cursor.execute(query)
		currencies = []
		for row in res.fetchall():
			currencies.append({'code': row[0], 'name': row[1]})
		template = Template(filename='home.html', output_encoding='utf-8', encoding_errors='replace')
		page = template.render(
			currencies = currencies,
			nick_taken = None,
			nick_not_valid = None,
			wrong_currency = None,
			nick = None,
			selected_currency = None)
		con.close()
		return page
	
	@cherrypy.expose
	def data(self, username=None):
		print "data| username=",username
		# there must be a username
		if not username:
			return demjson.encode({'error_code': 0})
		# connect to DB
		con = sqlite.connect('imfr.db')
		if not con:
			return demjson.encode({'error_code': 0})
		# the username must be valid
		if not isUsernameValid(con, username):
			con.close()
			return demjson.encode({'error_code': 0})
		# it's working ! let's load data
		cursor = con.cursor()
		
		query = "SELECT id, default_currency FROM USERS WHERE username=?"
		res = cursor.execute(query, (username, ))
		row = res.fetchone()
		user_id = row[0]
		default_currency = row[1]
		query = "SELECT date, amount, currency, given_by, why, notes, id FROM MONEY WHERE user_id=? ORDER BY date ASC"
		res = cursor.execute(query, (user_id, ))
		data = []
		for row in res.fetchall():
			r = {	'date': int(row[0]),
					'amount': int(row[1]),
					'amount_in_default_currency': 0,
					'currency': row[2],
					'given_by': row[3],
					'why': row[4],
					'notes': row[5],
					'id': row[6]}
			# convert amount to default currency
			m = convert(r['amount'], r['currency'], default_currency)
			if m != 'nocon' and m != 'nonvalidcurrency':
				r['amount_in_default_currency'] = m
			else:
				r['amount_in_default_currency'] = amount
				
			data.append(r)
		con.close()
		return demjson.encode({'error_code': 1,'data': data, 'default_currency': default_currency})

	@cherrypy.expose
	def newuser(self, username=None, currency=None, password=''):
		
		if username is None or currency is None:
			raise cherrypy.HTTPRedirect("/")
	
		# check connexion to DB
		con = sqlite.connect('imfr.db')
		if not con:
			return 'no_con'
		cursor = con.cursor()

		# check that nickname is ok
		nick_not_valid = False
		username = username.lower()
		username.strip()
		for c in username:
			if c not in "abcdefghijklmnopqrstuvwxyz0123456789":
				nick_not_valid = True

		# check nickname availability
		nick_taken = False
		if not nick_not_valid:
			query="SELECT count(*) FROM users WHERE username=?"
			res = cursor.execute(query, (username, ))
			n = int(res.fetchone()[0])
			if n != 0:
				nick_taken = True
			
		# check currency
		wrong_currency = False
		query = "SELECT count(*) FROM CURRENCIES WHERE code=?"
		res = cursor.execute(query, (currency, ))
		n = int(res.fetchone()[0])
		if n != 1:
			wrong_currency = True
		
		# if we got here, then it's fine
		if not (nick_taken or nick_not_valid or wrong_currency):
		
			password = password.lower().strip()
			m = md5.new()
			m.update(username)
			m.update(password)
			query = "INSERT INTO USERS(username, default_currency, password) VALUES (?, ?, ?)"
			res = cursor.execute(query, (username, currency, m.hexdigest()))
			con.commit()
				
		# return page with eventual error messages
		# get currencies
		query = "SELECT code, name FROM CURRENCIES ORDER BY name ASC"
		res = cursor.execute(query)
		currencies = []
		for row in res.fetchall():
			currencies.append({'code': row[0], 'name': row[1]})
		template = Template(filename='home.html', output_encoding='utf-8', encoding_errors='replace')
		page = template.render(
			currencies = currencies,
			nick_taken = nick_taken,
			nick_not_valid = nick_not_valid,
			wrong_currency = wrong_currency,
			nick = username,
			selected_currency = currency)
		con.close()
		return page
	
	@cherrypy.expose
	def transactionform(self, username=None, transactionID=None, status=None):

		# username must be specified
		if username is None:
			raise cherrypy.HTTPRedirect("/")
		
		# check connexion to DB
		con = sqlite.connect('imfr.db')
		if not con:
			return 'no_con'
		cursor = con.cursor()
		
		# check username
		username = username.lower().strip()
		if not isUsernameValid(con, username):
			con.close()
			raise cherrypy.HTTPRedirect("/")
		
		cursor = con.cursor()
		
		# load profile details
		query = "SELECT id, default_currency FROM USERS WHERE username=?"
		res = cursor.execute(query, (username, ))
		row = cursor.fetchone()
		userID = row[0]
		default_currency = row[1]
		
		# init variables
		amount = None
		formated_date = None
		currency = None
		given_by = None
		why = None
		notes = None
		
		if status is None:
			errors = {
				'amount_not_number': False,
				'wrong_currency': False,
				'no_date': False,
				'wrong_password': False}
			success = False
		else:
			errors = status['errors']
			success = status['success']
		
		# if the transaction is specified and valid, load transaction details
		if transactionID is not None:
			# check that id is valid
			query = "SELECT count(*) FROM MONEY WHERE id=? AND user_id=?"
			res = cursor.execute(query, (transactionID, userID))
			n = int(res.fetchone()[0])
			if n != 1:
				# not valid but still specified: did somebody try to mess up with me ?
				con.close()
				raise cherrypy.HTTPRedirect("/")
			# specified and valid, rock and roll !
			query = "SELECT amount, currency, given_by, date, why, notes FROM MONEY WHERE id=? and user_id=?"
			res = cursor.execute(query, (transactionID, userID))
			row = res.fetchone()
			amount = row[0]
			currency = row[1]
			given_by = row[2]
			# date needs formating
			date = row[3]
			d = datetime.fromtimestamp(date)
			month = d.month
			day = d.day
			year = d.year
			formated_date = str(month)+"/"+str(day)+"/"+str(year)
			why = row[4]
			notes = row[5]
		else:
			currency = default_currency
		
		# get currencies
		query = "SELECT code, name FROM CURRENCIES ORDER BY name ASC"
		res = cursor.execute(query)
		currencies = []
		for row in res.fetchall():
			currencies.append({'code': row[0], 'name': row[1]})
		
		# generate and return page
		template = Template(filename='form.html', output_encoding='utf-8', encoding_errors='replace')
		page = template.render(
			errors = errors,
			success = success,
			amount = amount,
			date = formated_date,
			currency = currency,
			given_by = given_by,
			why = why,
			notes = notes,
			currencies = currencies,
			default_currency = default_currency,
			transactionID = transactionID,
			username = username)
		con.close()
		return page
	
	@cherrypy.expose
	def savetransaction(self, username, password, transactionID, amount, currency, why, notes, given_by, date):
		
		errors = {
			'amount_not_number': False,
			'wrong_currency': False,
			'no_date': False,
			'wrong_password': False}
		success = False
		
		# username must be specified
		if username is None:
			raise cherrypy.HTTPRedirect("/")
		
		# check connexion to DB
		con = sqlite.connect('imfr.db')
		if not con:
			return 'no_con'
		cursor = con.cursor()
		
		# check username
		username = username.lower().strip()
		if not isUsernameValid(con, username):
			con.close()
			raise cherrypy.HTTPRedirect("/")
		
		# get userID
		query = "SELECT id, default_currency FROM USERS WHERE username=?"
		res = cursor.execute(query, (username, ))
		row = res.fetchone()
		userID = int(row[0])
		default_currency = row[1]
		
		# check password
		password = password.lower().strip()
		m = md5.new()
		m.update(username)
		m.update(password)
		query = "SELECT count(*) FROM USERS WHERE username=? AND id=? AND password=?"
		res = cursor.execute(query, (username, userID, m.hexdigest()))
		n = int(res.fetchone()[0])
		if n != 1:
			errors['wrong_password'] = True
		
		# check  transactionID
		if not (str(transactionID) == 'None'):
			query = "SELECT count(*) FROM MONEY WHERE id=? AND user_id=?"
			res = cursor.execute(query, (transactionID, userID))
			n = int(res.fetchone()[0])
			if n != 1:
				con.close()
				raise cherrypy.HTTPRedirect("/"+username)
		
		
		# check that amount is ok
		try:
			amount = float(amount)
		except:
			errors['amount_not_number'] = True
		
		# check currency
		query = "SELECT count(*) FROM CURRENCIES WHERE code=?"
		res = cursor.execute(query, (currency, ))
		n = int(res.fetchone()[0])
		if n != 1:
			errors['wrong_currency'] = True
		
		# process date
		formated_date = date
		fields = date.split('/')
		try:
			month = int(fields[0])
			day = int(fields[1])
			year = int(fields[2])
			date = datetime(year, month, day)
			date = time.mktime(date.timetuple())
		except:
			errors['no_date'] = True
		
		# no error were found:
		error_found = False
		for key in errors.keys():
			error_found = error_found or errors[key]
		
		if not error_found:
			# what do we need to do ? insert or edit ?
			if str(transactionID) == 'None':
				query = "INSERT INTO MONEY(user_id, amount, currency, why, notes, given_by, date) VALUES (?,?,?,?,?,?,?)"
				cursor.execute(query, (userID, amount, currency, why, notes, given_by, date))
				con.commit()
			else: 
				query = "UPDATE MONEY SET amount=?, currency=?, why=?, notes=?, given_by=?, date=? WHERE id=?"
				cursor.execute(query, (amount, currency, why, notes, given_by, date, transactionID))
				con.commit()
			# anyway, it's a success
			success = True
		
		# get currencies
		query = "SELECT code, name FROM CURRENCIES ORDER BY name ASC"
		res = cursor.execute(query)
		currencies = []
		for row in res.fetchall():
			currencies.append({'code': row[0], 'name': row[1]})
		
		
		template = Template(filename='form.html', output_encoding='utf-8', encoding_errors='replace')
		form = template.render(
			errors = errors,
			success = success,
			amount = amount,
			date = formated_date,
			currency = currency,
			given_by = given_by,
			why = why,
			notes = notes,
			currencies = currencies,
			default_currency = default_currency,
			transactionID = transactionID,
			username = username)

		con.close()
		return form
	
	@cherrypy.expose
	def deletetransaction(self, username, password, transactionID):
		
		errors = {
			'amount_not_number': False,
			'wrong_currency': False,
			'no_date': False,
			'wrong_password': False}
		success = False
		
		# username must be specified
		if username is None:
			raise cherrypy.HTTPRedirect("/")
		
		# check connexion to DB
		con = sqlite.connect('imfr.db')
		if not con:
			return 'no_con'
		cursor = con.cursor()
		
		# check username
		username = username.lower().strip()
		if not isUsernameValid(con, username):
			con.close()
			raise cherrypy.HTTPRedirect("/")
		
		# get userID
		query = "SELECT id, default_currency FROM USERS WHERE username=?"
		res = cursor.execute(query, (username, ))
		row = res.fetchone()
		userID = int(row[0])
		default_currency = row[1]
		
		# check password
		password = password.lower().strip()
		m = md5.new()
		m.update(username)
		m.update(password)
		query = "SELECT count(*) FROM USERS WHERE username=? AND id=? AND password=?"
		res = cursor.execute(query, (username, userID, m.hexdigest()))
		n = int(res.fetchone()[0])
		if n != 1:
			errors['wrong_password'] = True
		
		# check  transactionID
		if not (str(transactionID) == 'None'):
			query = "SELECT count(*) FROM MONEY WHERE id=? AND user_id=?"
			res = cursor.execute(query, (transactionID, userID))
			n = int(res.fetchone()[0])
			if n != 1:
				con.close()
				raise cherrypy.HTTPRedirect("/"+username)
				
		# no error were found:
		error_found = False
		for key in errors.keys():
			error_found = error_found or errors[key]
		
		if not error_found:
			query = "DELETE FROM MONEY WHERE id=? AND user_id=?"
			cursor.execute(query, (transactionID, userID))
			con.commit()
			success = True
			transactionID = None
		
		status = {
			'errors': errors,
			'success': success}
		con.close()
		return self.transactionform(username, transactionID, status)


cherrypy.config.update({
    'environment': 'production',
    'log.error_file': '/home/jeremy/logs/user/imfuckinrich/error_log',
    'log.screen': False,
    'server.socket_host': '127.0.0.1',
    'server.socket_port': 17606,
})

local_conf = { 
		'/css': {
			'tools.staticdir.on' : True,
			'tools.staticdir.dir' : '/local/path/I\'m fuckin rich/css'},
		'/js': {
			'tools.staticdir.on' : True,
			'tools.staticdir.dir' : '/local/path/I\'m fuckin rich/js/'},
		'/pix': {
			'tools.staticdir.on' : True,
			'tools.staticdir.dir' : '/local/path/I\'m fuckin rich/pix/'}}
global_conf = { 
		'/css': {
			'tools.staticdir.on' : True,
			'tools.staticdir.dir' : '/server/path/imfuckinrich/css'},
		'/js': {
			'tools.staticdir.on' : True,
			'tools.staticdir.dir' : '/server/path/imfuckinrich/js/'},
		'/pix': {
			'tools.staticdir.on' : True,
			'tools.staticdir.dir' : '/server/path/imfuckinrich/pix/'}}

cherrypy.quickstart(IMFR(), config=global_conf) 