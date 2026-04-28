-- Create the application database
CREATE DATABASE IF NOT EXISTS `database_app`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Create the application user and grant privileges
CREATE USER IF NOT EXISTS 'app'@'%' IDENTIFIED BY 'secret';
GRANT ALL PRIVILEGES ON `database_app`.* TO 'app'@'%';

-- Create a separate test database
CREATE DATABASE IF NOT EXISTS `database_app_test`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON `database_app_test`.* TO 'app'@'%';

FLUSH PRIVILEGES;