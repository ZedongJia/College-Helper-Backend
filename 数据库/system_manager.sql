CREATE SCHEMA system_manager;

CREATE  TABLE `user` ( 
	id                   BIGINT UNSIGNED NOT NULL   AUTO_INCREMENT  PRIMARY KEY,
	nickname             TEXT       ,
	password             TEXT       ,
	image                TEXT       ,
	phone                VARCHAR(50)       ,
	gender               ENUM('male','female','unknown')       ,
	email                VARCHAR(100)       ,
	QQ                   VARCHAR(100)       ,
	weChat               VARCHAR(100)       
 ) engine=InnoDB;

CREATE  TABLE browsing_history ( 
	id                   BIGINT UNSIGNED NOT NULL   AUTO_INCREMENT  PRIMARY KEY,
	user_id              BIGINT UNSIGNED NOT NULL     ,
	`time`               TIMESTAMP       ,
	`type`               VARCHAR(20)       ,
	content              TEXT       ,
	isCollected          ENUM('true','false')   DEFAULT ('false')    ,
	isHistory            ENUM('true','false')   DEFAULT ('true')    
 ) engine=InnoDB;

CREATE  TABLE feedback ( 
	id                   BIGINT UNSIGNED NOT NULL   AUTO_INCREMENT  PRIMARY KEY,
	user_id              BIGINT UNSIGNED NOT NULL     ,
	`time`               TIMESTAMP       ,
	`type`               VARCHAR(20)       ,
	question             TEXT       ,
	advice               TEXT       ,
	image                BLOB       ,
	state                VARCHAR(20)       
 ) engine=InnoDB;

CREATE  TABLE follow ( 
	user_id              BIGINT UNSIGNED NOT NULL     ,
	follow_id            BIGINT UNSIGNED NOT NULL     
 ) engine=InnoDB;

CREATE  TABLE gallery ( 
	user_id              BIGINT UNSIGNED NOT NULL     ,
	image                MEDIUMBLOB  NOT NULL     
 ) engine=InnoDB;

CREATE  TABLE message ( 
	session_id           BIGINT UNSIGNED NOT NULL     ,
	user_id              BIGINT UNSIGNED NOT NULL     ,
	`time`               TIMESTAMP       ,
	content              TEXT       
 ) engine=InnoDB;

CREATE  TABLE privacy ( 
	user_id              BIGINT UNSIGNED NOT NULL     ,
	telephone_priv       ENUM('true','false')   DEFAULT ('false')    ,
	gender_priv          ENUM('true','false')   DEFAULT ('false')    ,
	email_priv           ENUM('true','false')   DEFAULT ('false')    ,
	QQ_priv              ENUM('true','false')   DEFAULT ('false')    ,
	weChat_priv          ENUM('true','false')   DEFAULT ('false')    ,
	collection_priv      ENUM('true','false')   DEFAULT ('false')    
 ) engine=InnoDB;

CREATE  TABLE review ( 
	id                   BIGINT UNSIGNED NOT NULL   AUTO_INCREMENT  PRIMARY KEY,
	user_id              BIGINT UNSIGNED NOT NULL     ,
	name                 TEXT       ,
	label                VARCHAR(100)       ,
	`time`               TIMESTAMP       ,
	content              TEXT       
 ) engine=InnoDB;

CREATE  TABLE session ( 
	id                   BIGINT UNSIGNED NOT NULL     ,
	user_id              BIGINT UNSIGNED NOT NULL     
 ) engine=InnoDB;

ALTER TABLE browsing_history ADD CONSTRAINT fk_browsing_history_user FOREIGN KEY ( user_id ) REFERENCES `user`( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE feedback ADD CONSTRAINT fk_feedback_user FOREIGN KEY ( user_id ) REFERENCES `user`( id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE follow ADD CONSTRAINT fk_follow_user FOREIGN KEY ( follow_id ) REFERENCES `user`( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE follow ADD CONSTRAINT fk_user FOREIGN KEY ( user_id ) REFERENCES `user`( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE gallery ADD CONSTRAINT fk_gallery_user FOREIGN KEY ( user_id ) REFERENCES `user`( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE message ADD CONSTRAINT fk_message_user FOREIGN KEY ( user_id ) REFERENCES `user`( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE privacy ADD CONSTRAINT fk_privacy_user FOREIGN KEY ( user_id ) REFERENCES `user`( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE review ADD CONSTRAINT fk_review_user FOREIGN KEY ( user_id ) REFERENCES `user`( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE session ADD CONSTRAINT fk_session_user FOREIGN KEY ( user_id ) REFERENCES `user`( id ) ON DELETE CASCADE ON UPDATE CASCADE;

delimiter $$
CREATE DEFINER = CURRENT_USER TRIGGER `system_manager`.`user_AFTER_INSERT` AFTER INSERT ON `user` FOR EACH ROW
BEGIN
INSERT INTO privacy VALUES(NEW.id, 'true', 'true', 'true', 'true', 'true', 'true');
END $$
delimiter ;
