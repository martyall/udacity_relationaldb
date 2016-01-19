-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE players(
  id SERIAL,
  name TEXT,
  PRIMARY KEY(id)
);

CREATE TABLE matches(
  home REFERENCES players (id),
  visitor REFERENCES players (id),
  round INTEGER,
  PRIMARY KEY(home, visitor, round)
);
