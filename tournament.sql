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
  match_id SERIAL
  home SERIAL REFERENCES players (id),
  visitor SERIAL REFERENCES players (id),
  winner SERIAL REFERENCES players (id),
  PRIMARY KEY(match_id),
  CHECK ((winner = home) OR (winner = visitor))
);
