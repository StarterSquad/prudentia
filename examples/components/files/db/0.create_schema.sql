CREATE DATABASE IF NOT EXISTS `app_db`;

CREATE USER 'app'@'localhost' IDENTIFIED BY 'I4mth3p4ssw0rd';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,INDEX ON `app_db`.* TO 'app'@'localhost';
CREATE USER 'app'@'%' IDENTIFIED BY 'I4mth3p4ssw0rd';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,INDEX ON `app_db`.* TO 'app'@'%';

USE `app_db`;

CREATE TABLE `flights` (
  `id` VARCHAR(255) NOT NULL,
  `search_time` DATETIME NOT NULL,
  `price` VARCHAR(50) NOT NULL,
  `seat_class` VARCHAR(50) NOT NULL,
  `out_airport_code` VARCHAR(5) NOT NULL,
  `out_airport_name` VARCHAR(100) NOT NULL,
  `out_carrier` VARCHAR(50) NOT NULL,
  `out_equipment` VARCHAR(100),
  `out_flight_number` INT NOT NULL,
  `out_departure_date` DATE NOT NULL,
  `out_departure_time` TIME NOT NULL,
  `out_arrival_time` VARCHAR(50) NOT NULL,
  `out_duration` VARCHAR(50) NOT NULL,
  `out_seats_left` VARCHAR(50),
  `out_extra` VARCHAR(500),
  `ret_airport_code` VARCHAR(5) NOT NULL,
  `ret_airport_name` VARCHAR(100) NOT NULL,
  `ret_carrier` VARCHAR(50) NOT NULL,
  `ret_flight_number` INT NOT NULL,
  `ret_equipment` VARCHAR(100),
  `ret_departure_date` DATE NOT NULL,
  `ret_departure_time` TIME NOT NULL,
  `ret_arrival_time` VARCHAR(50) NOT NULL,
  `ret_duration` VARCHAR(50) NOT NULL,
  `ret_seats_left` VARCHAR(50),
  `ret_extra` VARCHAR(500),
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;
