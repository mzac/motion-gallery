# motion-gallery

# motion-gallery

This simple cgi script allows you to see the last 8 images captured by Motion
as well as the 'lastsnap'

It also links to the videos captured that go along with the images.

There are some dependencies:

- Motion (http://www.lavrsen.dk/foswiki/bin/view/Motion)
- MySQL
- Web server (tested on Apache)
- Perl and the following modules
	- DateTime
	- Date::Simple
	- DBI

To setup the motion database, create a MySQL table with the following:

```
mysqladmin -p create motion

mysql -p motion

CREATE TABLE `security` (
	`camera` INT(11) NULL DEFAULT NULL,
	`filename` CHAR(80) NOT NULL,
	`frame` INT(11) NULL DEFAULT NULL,
	`file_type` INT(11) NULL DEFAULT NULL,
	`time_stamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`event_time_stamp` TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00'
);
```

You will also have to add a user to your MySQL database to allow motion to talk to the database

```
mysql -p
GRANT SELECT, INSERT, UPDATE, DELETE, DROP, CREATE VIEW, INDEX, EXECUTE ON motion.* TO 'motion'@'localhost' IDENTIFIED BY 'motion';
flush privileges;
```

In your motion setup, you will need to add lines such as this to your ~~motion.conf~~ to allow motion to talk to the database

```
sql_log_picture on
sql_log_snapshot off
sql_log_movie on
sql_log_timelapse off
sql_query insert into security(camera, filename, frame, file_type, time_stamp, event_time_stamp) values('%t', '%f', '%q', '%n', '%Y-%m-%d %T', '%C')

database_type mysql
database_dbname motion
database_host 127.0.0.1
database_user motion
database_password motion
database_port 3306
```

Make sure to restart your motion daemon after the change to the config file.

For your web server to be able to execute the script, you will need to give permissions to execute in the directory where you put the ~~index.cgi~~ file

This is an example for Apache:

```
<Directory /var/www/html/rc >
	SetHandler cgi-script
	Options ExecCGI
</Directory>
```
