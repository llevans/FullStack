-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Drop tables
DROP TABLE IF EXISTS Match;
DROP TABLE IF EXISTS Tournament;
DROP TABLE IF EXISTS Player;

-- Players
CREATE TABLE Player (id SERIAL, full_name VARCHAR(60), CONSTRAINT playerPK PRIMARY KEY (id));

--Tournaments
CREATE TABLE Tournament (id SERIAL, description VARCHAR(200), CONSTRAINT tournamentPK PRIMARY KEY (id));

--Matches
CREATE TABLE Match (id SERIAL, player1 INTEGER, player2 INTEGER, winner INTEGER, round INTEGER, tournament INTEGER, CONSTRAINT player1FK FOREIGN KEY (player1) REFERENCES Player (id), CONSTRAINT player2FK FOREIGN KEY (player2) REFERENCES Player (id), CONSTRAINT tournamentFK FOREIGN KEY (tournament) REFERENCES Tournament (id));

