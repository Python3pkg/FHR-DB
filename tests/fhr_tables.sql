CREATE TABLE `simple_field1_index` (
  `id` INT(22) NOT NULL auto_increment,
  `field1` VARCHAR(64) NOT NULL,
  `simple_id` INT(22) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY (`field1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `simple_field_double_index` (
  `id` INT(22) NOT NULL auto_increment,
  `field1` VARCHAR(64) NOT NULL,
  `field2` VARCHAR(64) NOT NULL,
  `simple_id` INT(22) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY (`field1`, `field2`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `simple_inner_index` (
  `id` INT(22) NOT NULL auto_increment,
  `field1_inner` VARCHAR(64) NOT NULL,
  `simple_id` INT(22) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY (`field1_inner`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `complex_inner_model` (
  `id` INT(22) NOT NULL auto_increment,
  `body` TEXT NOT NULL,
  `updated` TIMESTAMP NOT NULL,
  `created` TIMESTAMP NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `simple_token_index` (
  `id` INT(22) NOT NULL auto_increment,
  `email_token` VARCHAR(64) NOT NULL,
  `simple_id` INT(22) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY (`email_token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `simple_new_index` (
  `id` INT(22) NOT NULL auto_increment,
  `new` VARCHAR(64) NOT NULL,
  `simple_id` INT(22) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY (`new`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `simple_new_new2_index` (
  `id` INT(22) NOT NULL auto_increment,
  `new` VARCHAR(64) NOT NULL,
  `new2` VARCHAR(64) NOT NULL,
  `simple_id` INT(22) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY (`new`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `simple_new_new2_new3_index` (
  `id` INT(22) NOT NULL auto_increment,
  `new` VARCHAR(64) NOT NULL,
  `new2` VARCHAR(64) NOT NULL,
  `new3` VARCHAR(64) NOT NULL,
  `simple_id` INT(22) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY (`new`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `simple_updated_index` (
  `id` INT(22) NOT NULL auto_increment,
  `updated` DATETIME NOT NULL,
  `simple_id` INT(22) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY (`updated`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `simple_created_index` (
  `id` INT(22) NOT NULL auto_increment,
  `created` DATETIME NOT NULL,
  `simple_id` INT(22) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY (`created`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;