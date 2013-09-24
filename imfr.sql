DROP TABLE USERS;
CREATE TABLE USERS(
	id INTEGER PRIMARY KEY,
	username TEXT,
	default_currency TEXT,
	password TEXT
);

INSERT INTO USERS(username, default_currency, password) VALUES ('jeremy', 'EUR', '20aa75ae58e076558ce07546464b82ee');
INSERT INTO USERS(username) VALUES('default');
INSERT INTO USERS(username) VALUES('data');
INSERT INTO USERS(username) VALUES('newuser');
INSERT INTO USERS(username) VALUES('transactionform');
INSERT INTO USERS(username) VALUES('deletransaction');
INSERT INTO USERS(username) VALUES('savetransaction');


DROP TABLE MONEY;
CREATE TABLE MONEY(
	id INTEGER PRIMARY KEY,
	user_id INTEGER,
	amount INTEGER,
	currency TEXT,
	given_by TEXT,
	why TEXT,
	notes TEXT,
	date TIMESTAMP
);

INSERT INTO MONEY(user_id, amount, currency, given_by, why, notes, date) VALUES (1, 1000000, 'EUR', 'bank of nigeria', 'death of ex-dictator', 'she needs it so badly!', '1262304000');
INSERT INTO MONEY(user_id, amount, currency, given_by, why, notes, date) VALUES (1, 30000, 'USD', 'branco di coglioni', 'for fun', 'bouh', '1264982400');
INSERT INTO MONEY(user_id, amount, currency, given_by, why, notes, date) VALUES (1, 60000000, 'USD', 'branco di coglioni', 'for fun', 'bouh', '1267401600');

DROP TABLE CURRENCIES;
CREATE TABLE CURRENCIES (
	id INTEGER PRIMARY KEY,
	code TEXT,
	name TEXT,
	rate_to_euro FLOAT 
	
);

INSERT INTO CURRENCIES(code, name, rate_to_euro) VALUES ('EUR', 'Euro', 1);