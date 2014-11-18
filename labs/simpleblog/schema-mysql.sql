DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
	id INT(10) unsigned NOT NULL auto_increment,
	title VARCHAR(30) NOT NULL default '',
	subtitle VARCHAR(30) NOT NULL default '',
	content TEXT,
	posted_on timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
	PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
	id INT(10) unsigned NOT NULL auto_increment,
	name VARCHAR(32) NOT NULL default '',
	password VARCHAR(32) NOT NULL default '',
	create_time timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
    UNIQUE KEY(name)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
