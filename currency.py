import sqlite3 as sqlite
#from pysqlite2 import dbapi2 as sqlite
import urllib2


def convert(amount, from_currency, to_currency):
	con = sqlite.connect('imfr.db')
	if not con:
		return 'nocon'
	cursor = con.cursor()
	# check that codes are ok
	query = "SELECT count(*) FROM CURRENCIES WHERE code=?"
	res = cursor.execute(query, (from_currency, ))
	n_from = int(res.fetchone()[0])
	query = "SELECT count(*) FROM CURRENCIES WHERE code=?"
	res = cursor.execute(query, (to_currency, ))
	n_to = int(res.fetchone()[0])
	if n_from != 1 or n_to != 1:
		return 'nonvalidcurrency'
	# everything is all right, select rates
	query = "SELECT rate_to_euro FROM CURRENCIES WHERE code=?"
	res = cursor.execute(query, (from_currency, ))
	from_rate = float(res.fetchone()[0])
	query = "SELECT rate_to_euro FROM CURRENCIES WHERE code=?"
	res = cursor.execute(query, (to_currency, ))
	to_rate = float(res.fetchone()[0])
	return amount * (to_rate / from_rate)
	
def update_db():
	# connect to DB
	con = sqlite.connect('imfr.db')
	if not con:
		return -1
	cursor = con.cursor()
	# retrieve rates
	rates = []
	data_url = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
	xml_data = urllib2.urlopen(data_url)
	for line in xml_data.readlines():
		if "currency" in line:
			code = line[line.find("currency='")+10:line.find("' rate")]
			rate = float(line[line.find("rate='")+6: line.find("'/>")])
			rates.append({'code': code, 'rate': rate, 'name': ''})
	# update DB
	for rate in rates:
		query = "SELECT count(*) FROM CURRENCIES WHERE code=?"
		res = cursor.execute(query, (rate['code'], ))
		n = int(res.fetchone()[0])
		# it exists, update entry
		if n == 1:
			query = "UPDATE CURRENCIES SET rate_to_euro=? WHERE code=?"
			cursor.execute(query, (rate['rate'], rate['code']))
		# it doesn't exist, insert entry
		if n == 0:
			query = "INSERT INTO CURRENCIES (code, name, rate_to_euro) VALUES(?,?,?)"
			cursor.execute(query, (rate['code'], rate['name'], rate['rate']))
		# there is more than one: erase them all and then insert Value
		if n >= 2:
			query = "DELETE FROM CURRENCIES WHERE code=?"
			cursor.execute(query, (rate['code']))
			query = "INSERT INTO CURRENCIES (code, name, rate_to_euro) VALUES(?,?,?)"
			cursor.execute(query, (rate['code'], rate['name'], rate['rate']))
		con.commit()
	
def set_names():
	currencies = [
		{'code': 'USD', 'name': 'US Dollars'},
		{'code': 'JPY', 'name': 'Japanese Yen'},
		{'code': 'BGN', 'name': 'Bulgarian Lev'},
		{'code': 'CZK', 'name': 'Czech Koruna'},
		{'code': 'DKK', 'name': 'Denmark Kroner'},
		{'code': 'EEK', 'name': 'Estonian Kroon'},
		{'code': 'GBP', 'name': 'British Pounds Sterling'},
		{'code': 'HUF', 'name': 'Hungarian Forint'},
		{'code': 'LTL', 'name': 'Lithuanian Litas'},
		{'code': 'LVL', 'name': 'Latvian Lats'},
		{'code': 'PLN', 'name': 'Polish New Zloty'},
		{'code': 'RON', 'name': 'New Romanian Leu'},
		{'code': 'SEK', 'name': 'Sweden Kronor'},
		{'code': 'CHF', 'name': 'Swiss Francs'},
		{'code': 'NOK', 'name': 'Norway Kroner'},
		{'code': 'HRK', 'name': 'Croatian Kuna'},
		{'code': 'RUB', 'name': 'Russian Rouble'},
		{'code': 'TRY', 'name': 'New Turkish Lira'},
		{'code': 'AUD', 'name': 'Australian Dollars'},
		{'code': 'BRL', 'name': 'Brazilian Real'},
		{'code': 'CAD', 'name': 'Canadian Dollars'},
		{'code': 'CNY', 'name': 'Yuan Renminbi'},
		{'code': 'HKD', 'name': 'Hong Kong Dollars'},
		{'code': 'IDR', 'name': 'Indonesian Rupiah'},
		{'code': 'INR', 'name': 'Indian Rupee'},
		{'code': 'KRW', 'name': 'South Korean Won'},
		{'code': 'MXN', 'name': 'Mexico Peso'},
		{'code': 'MYR', 'name': 'Malaysian Ringgit'},
		{'code': 'NZD', 'name': 'New Zealand Dollars'},
		{'code': 'PHP', 'name': 'Philippine Peso'},
		{'code': 'SGD', 'name': 'Singapore Dollars'},
		{'code': 'THB', 'name': 'Thai Baht'},
		{'code': 'ZAR', 'name': 'South African Rand'},
		{'code': 'EUR', 'name': 'Euro'}
	]
	# connect to DB
	con = sqlite.connect('imfr.db')
	if not con:
		return -1
	cursor = con.cursor()
	# update entries
	for currency in currencies:
		query = "UPDATE CURRENCIES SET name=? WHERE code=?"
		res = cursor.execute(query, (currency['name'], currency['code']))
	con.commit()