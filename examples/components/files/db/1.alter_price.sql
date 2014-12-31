USE `app_db`;

ALTER TABLE `flights` ADD `price_int` INT NOT NULL;

UPDATE `flights` set `price_int` = CONVERT(price, UNSIGNED INTEGER);

ALTER TABLE `flights` DROP `price`;

ALTER TABLE `flights` CHANGE `price_int` `price` INT NOT NULL;
