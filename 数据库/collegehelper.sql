CREATE SCHEMA college_helper;

CREATE  TABLE main_branch ( 
	id                   INT UNSIGNED NOT NULL     PRIMARY KEY,
	name                 VARCHAR(100)       ,
	tag                  TINYTEXT       ,
	infoDict             JSON       ,
	intro                TEXT       
 ) engine=InnoDB;

CREATE  TABLE province ( 
	id                   INT UNSIGNED NOT NULL     PRIMARY KEY,
	name                 VARCHAR(100)       
 ) engine=InnoDB;

CREATE  TABLE special ( 
	id                   INT UNSIGNED NOT NULL     PRIMARY KEY,
	name                 TEXT       ,
	tag                  TINYTEXT       ,
	infoDict             JSON       ,
	intro                TEXT       
 ) engine=InnoDB;

CREATE  TABLE sub_branch ( 
	id                   INT UNSIGNED NOT NULL     PRIMARY KEY,
	fk_mainBranch_id     INT UNSIGNED NOT NULL     ,
	name                 TEXT(100)       ,
	tag                  TINYTEXT       ,
	infoDict             JSON       ,
	intro                TEXT       
 ) engine=InnoDB;

CREATE  TABLE city ( 
	id                   INT UNSIGNED NOT NULL     PRIMARY KEY,
	name                 VARCHAR(100)  NOT NULL     ,
	fk_province_id       INT UNSIGNED NOT NULL     
 ) engine=InnoDB;

CREATE  TABLE fractional_line ( 
	id                   INT UNSIGNED NOT NULL     PRIMARY KEY,
	fk_province_id       INT UNSIGNED NOT NULL     ,
	year                 VARCHAR(5)       ,
	category             VARCHAR(20)       ,
	degree               VARCHAR(50)       ,
	detail               JSON       
 ) engine=InnoDB;

CREATE  TABLE university ( 
	id                   INT UNSIGNED NOT NULL     PRIMARY KEY,
	fk_city_id           INT UNSIGNED NOT NULL     ,
	name                 TEXT  NOT NULL     ,
	imageUrls            JSON       ,
	establishTime        VARCHAR(100)       ,
	detailLocation       TEXT       ,
	honorTags            JSON       ,
	officialWebsite      JSON       ,
	officialPhoneNumber  JSON       ,
	officialEmail        VARCHAR(100)       ,
	rankInfo             JSON       ,
	educationInfo        JSON       ,
	intro                JSON       
 ) engine=InnoDB;

CREATE  TABLE living_condition ( 
	id                   INT UNSIGNED NOT NULL   AUTO_INCREMENT  PRIMARY KEY,
	fk_university_id     INT UNSIGNED NOT NULL     ,
	domitory             TEXT       ,
	canteen              TEXT       ,
	imageUrls            TEXT       
 ) engine=InnoDB;

CREATE  TABLE major ( 
	id                   INT UNSIGNED NOT NULL     PRIMARY KEY,
	fk_university_id     INT UNSIGNED NOT NULL     ,
	fk_sub_branch_id     INT UNSIGNED NOT NULL     ,
	name                 TEXT       ,
	degree               VARCHAR(20)       ,
	ruanKeScore          VARCHAR(50)       ,
	duration             VARCHAR(50)       ,
	careerInfo           TEXT       ,
	detail               TEXT       
 ) engine=InnoDB;

CREATE  TABLE major_line ( 
	fk_major_id          INT UNSIGNED NOT NULL     ,
	fk_province_id       INT UNSIGNED NOT NULL     ,
	year                 VARCHAR(5)       ,
	branch               VARCHAR(50)       ,
	batch                VARCHAR(100)       ,
	lowScore             VARCHAR(100)       ,
	averageScore         VARCHAR(100)       
 ) engine=InnoDB;

CREATE  TABLE person ( 
	id                   INT UNSIGNED NOT NULL   AUTO_INCREMENT  PRIMARY KEY,
	fk_university_id     INT UNSIGNED NOT NULL     ,
	name                 VARCHAR(100)       ,
	identity             VARCHAR(50)       ,
	tag                  TINYTEXT       ,
	infoDict             JSON       ,
	intro                TEXT       
 ) engine=InnoDB;

CREATE  TABLE rel_main_branch_university ( 
	fk_university_id     INT UNSIGNED NOT NULL     ,
	fk_main_branch       INT UNSIGNED NOT NULL     
 ) engine=InnoDB;

CREATE  TABLE rel_university_special ( 
	fk_university_id     INT UNSIGNED NOT NULL     ,
	fk_special_id        INT UNSIGNED NOT NULL     
 ) engine=InnoDB;

CREATE  TABLE total_line ( 
	fk_university_id     INT UNSIGNED NOT NULL     ,
	fk_province_id       INT UNSIGNED NOT NULL     ,
	year                 VARCHAR(5)       ,
	branch               VARCHAR(50)       ,
	batch                VARCHAR(100)       ,
	controlScore         VARCHAR(100)       ,
	lowScore             VARCHAR(100)       ,
	enrollmentType       VARCHAR(50)       
 ) engine=InnoDB;

ALTER TABLE city ADD CONSTRAINT fk_city_province FOREIGN KEY ( fk_province_id ) REFERENCES province( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE fractional_line ADD CONSTRAINT fk_province FOREIGN KEY ( fk_province_id ) REFERENCES province( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE living_condition ADD CONSTRAINT fk_living_condition_university FOREIGN KEY ( fk_university_id ) REFERENCES university( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE major ADD CONSTRAINT fk_major_university FOREIGN KEY ( fk_university_id ) REFERENCES university( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE major_line ADD CONSTRAINT fk_major_line_province FOREIGN KEY ( fk_province_id ) REFERENCES province( id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE major_line ADD CONSTRAINT fk_major_line_major FOREIGN KEY ( fk_major_id ) REFERENCES major( id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE person ADD CONSTRAINT fk_person_university FOREIGN KEY ( fk_university_id ) REFERENCES university( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE rel_main_branch_university ADD CONSTRAINT fk_university FOREIGN KEY ( fk_university_id ) REFERENCES university( id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE rel_main_branch_university ADD CONSTRAINT fk_main_branch FOREIGN KEY ( fk_main_branch ) REFERENCES main_branch( id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE rel_university_special ADD CONSTRAINT fk_rel_university FOREIGN KEY ( fk_university_id ) REFERENCES university( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE rel_university_special ADD CONSTRAINT fk_rel_special FOREIGN KEY ( fk_special_id ) REFERENCES special( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE sub_branch ADD CONSTRAINT fk_branch_main_branch FOREIGN KEY ( fk_mainBranch_id ) REFERENCES main_branch( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE total_line ADD CONSTRAINT fk_university_policy FOREIGN KEY ( fk_university_id ) REFERENCES university( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE total_line ADD CONSTRAINT fk_province_policy FOREIGN KEY ( fk_province_id ) REFERENCES province( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE university ADD CONSTRAINT fk_university_city FOREIGN KEY ( fk_city_id ) REFERENCES city( id ) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE total_line MODIFY branch VARCHAR(50)     COMMENT '文科、理科、综合、物理、历史';

ALTER TABLE total_line MODIFY batch VARCHAR(100)     COMMENT '本科一批、本科二批';
