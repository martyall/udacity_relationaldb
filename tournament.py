#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    cursor = db.cursor()
    cursor.execute("DELETE FROM matches;")
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    cursor = db.cursor()
    cursor.execute("DELETE FROM players;")
    db.commit()
    db.close()

def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM players;")
    n_players = cursor.fetchall()[0][0]
    db.close()
    return n_players

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    cursor = db.cursor()
    cursor.execute("INSERT INTO players (name) VALUES (%s);", (name,))
    db.commit()
    db.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    cursor = db.cursor()
    query = """
        SELECT players.id, players.name, 
        sum(CASE WHEN (matches.winner = players.id) THEN 1 ELSE 0 END) AS wins, 
        sum(CASE WHEN (matches.winner IS NOT NULL) THEN 1 ELSE 0 END) AS matches FROM
        players JOIN
        matches
        ON (players.id = matches.home) OR (players.id = matches.visitor)
        GROUP BY players.id;
        """
    cursor.execute(query)
    stats = cursor.fetchall()
    have_played = set(map(lambda x: (x[0], x[1]), stats))
    # now we have to get everyone who hasn't played a match yet and put them in
    cursor.execute("SELECT players.id, players.name from players;")
    players = set(cursor.fetchall())
    havent_played = players - have_played
    stats = stats + map(lambda x: (x[0], x[1], 0, 0), list(havent_played))
    db.close()
    return stats

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    cursor = db.cursor()
    query = """
        INSERT INTO matches (home, visitor, winner)
        VALUES (%s, %s, %s);
        """
    cursor.execute(query, (winner, loser, winner))
    db.commit()
    db.close()

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db = connect()
    cursor = db.cursor()
    query = """
        SELECT a.id, a.name from (
            SELECT players.id, players.name,
            sum(CASE WHEN (matches.winner = players.id) THEN 1 ELSE 0 END) as wins, 
            sum(CASE WHEN (MATCHES.winner IS NOT NULL) THEN 1 ELSE 0 END) as matches from
            players JOIN
            matches
            ON (players.id = matches.home) OR (players.id = matches.visitor)
            GROUP BY players.id
            ORDER BY wins
            ) as a;
        """
    cursor.execute(query)
    players_with_wins = cursor.fetchall()
    db.close()
    matches = split_into_matches(players_with_wins, acc=[])
    return matches


def split_into_matches(players, acc):
    if players == []:
        return acc
    else:
        match = (players[0][0], players[0][1], players[1][0], players[1][1]) 
        return split_into_matches(players[2:], acc + [match])
