/*CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    title TEXT,
    subtitle TEXT,
    content TEXT,
    posted_on DATETIME
);*/
CREATE TABLE IF NOT EXISTS entries (
	id INT(10) unsigned NOT NULL auto_increment,
	title VARCHAR(30) NOT NULL default '',
	subtitle VARCHAR(30) NOT NULL default '',
	content TEXT,
	posted_on timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
	PRIMARY KEY (id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
