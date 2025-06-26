CREATE TABLE DBManagers (
	username varchar(255) PRIMARY KEY,
    password varchar(255)
);

CREATE TABLE Coaches (
	username varchar(255) PRIMARY KEY,
    password varchar(255),
    name varchar(255),
    surname varchar(255),
    nationality varchar(255)
);

CREATE TABLE Arbiters (
	username varchar(255) PRIMARY KEY,
    password varchar(255),
    name varchar(255),
    surname varchar(255),
    nationality varchar(255),
    experience_level ENUM('Beginner', 'Intermediate', 'Advanced', 'Expert')
);

CREATE TABLE Players (
	username varchar(255) PRIMARY KEY,
    password varchar(255),
    name varchar(255),
    surname varchar(255),
    nationality varchar(255),
    date_of_birth DATE,
    fide_id varchar(255),
    elo_rating INT,
    title ENUM('Grandmaster', 'International Master', 'FIDE Master', 'Candidate Master', 'National Master')
);

CREATE TABLE Halls (
	hall_id INT AUTO_INCREMENT PRIMARY KEY,
    hall_name varchar(255),
    country varchar(255),
    capacity INT
);

CREATE TABLE Tables (
	table_id INT AUTO_INCREMENT PRIMARY KEY,
    hall_id INT NOT NULL
);

CREATE TABLE Teams (
	team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name varchar(255)
);

CREATE TABLE Matches (
	match_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    time_slot ENUM('1', '2', '3'),
    hall_id INT NOT NULL,
    table_id INT NOT NULL,
    team1_id INT NOT NULL,
    team2_id INT NOT NULL,
    arbiter_username varchar(255) NOT NULL,
    ratings INT,
    white_player varchar(255) NOT NULL,
    black_player varchar(255),
    result ENUM('white wins', 'black wins', 'draw'),
    coach_username varchar(255),
    UNIQUE (white_player, date, time_slot),
    UNIQUE (black_player, date, time_slot),
    UNIQUE (arbiter_username, date, time_slot),
    UNIQUE (table_id, date, time_slot)
);

CREATE TABLE PlayerTeams (
	username varchar(255),
    team_id INT,
    PRIMARY KEY (username, team_id)
);

CREATE TABLE CoachCertifications (
	username varchar(255),
    certification varchar(255),
    PRIMARY KEY (username, certification)
);

CREATE TABLE ArbiterCertifications (
	username varchar(255),
    certification varchar(255),
    PRIMARY KEY (username, certification)
);

CREATE TABLE CoachTeams (
	username varchar(255),
    team_id INT,
    contract_start DATE,
    contract_finish DATE,
    PRIMARY KEY (username, team_id, contract_start)
);