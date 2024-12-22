CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(200) NOT NULL,
    phone_no VARCHAR(15) NOT NULL UNIQUE,
    status ENUM('active', 'inactive', 'banned') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS PlantInfo (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    CommonName VARCHAR(255),
    ScientificName VARCHAR(255),
    `Year` INT,
    Author VARCHAR(255),
    Status VARCHAR(50),
    `Rank` VARCHAR(50),
    FamilyCommonName VARCHAR(255),
    Genus VARCHAR(255),
    ImageURL TEXT,
    Edible TINYINT(1),
    SaplingDescription TEXT,
    PlantDescription TEXT
);
