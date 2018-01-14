CREATE DATABASE project;
USE project;

CREATE TABLE Users
(
	user_ID int4 AUTO_INCREMENT UNIQUE,
	first_name varchar(255),
	last_name varchar(255),
	email varchar(255) UNIQUE,
	date_of_birth DATE,
	hometown varchar(255),
	gender varchar(255),
	password varchar(255),
	PRIMARY KEY (user_ID),
	album_num int4
);

CREATE TABLE Friends (
	count int4 AUTO_INCREMENT,
	user_ID int4, 
    user_ID2 int4,
	FOREIGN KEY(user_ID) REFERENCES Users(user_ID) ON DELETE CASCADE,
    FOREIGN KEY(user_ID2) REFERENCES Users(user_ID) ON DELETE CASCADE,
    primary key(count)
);

CREATE TABLE Albums (
	album_ID int4 AUTO_INCREMENT UNIQUE,
	name varchar(255),
	date_of_creation DATE,
	PRIMARY KEY (album_ID),
    user_ID int4,
    photo_ID int4
);

CREATE TABLE Photos (
	photo_ID int4 AUTO_INCREMENT UNIQUE,
	caption varchar(255),
	data longblob,
	PRIMARY KEY (photo_ID),
    album_ID int4,
    FOREIGN KEY (album_ID) REFERENCES Albums(album_ID) ON DELETE CASCADE,
    comment_ID int4
	
);

CREATE TABLE Tags (
	tag_ID int4 AUTO_INCREMENT,
	text TEXT,
	PRIMARY KEY (Tag_ID)
);

CREATE TABLE Photo_Tag (
	count int4 AUTO_INCREMENT,
    photo_ID int4,
	tag_ID int4,
	PRIMARY KEY (count)
);

CREATE TABLE Comments (
	comment_ID int4 Auto_increment UNIQUE,
	Text TEXT,
	user_ID int4,
	Date DATE,
	PRIMARY KEY (comment_ID),
	photo_ID int4
);

CREATE TABLE Likes (
	photo_id int4,
	user_id int4,
	primary key(photo_id,user_id)
);

ALTER TABLE Albums ADD FOREIGN KEY (user_ID) REFERENCES Users(user_ID) ON DELETE CASCADE;
