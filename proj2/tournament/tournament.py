#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

##
def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    db = psycopg2.connect("dbname=tournament")
    cursor = db.cursor()
    return db, cursor


def deleteMatches():
    """Remove all the matches from the database."""
    db, cursor = connect()
    cursor.execute("TRUNCATE Match")
    db.commit()

def deleteTourMatches(tournament):
    """Remove all the match records in a tournament from the database."""
    db, cursor = connect()
    cursor.execute("DELETE FROM Match WHERE tournament = %s", (tournament,))
    db.commit()


def deletePlayers():
    """Remove all the player records from the database."""
    db, cursor = connect()
    cursor.execute("DELETE FROM Player")
    db.commit()


def deleteTournaments():
    """Remove all the player records from the database."""
    db, cursor = connect()
    cursor.execute("DELETE FROM Tournament")
    db.commit()


def countPlayers():
    """Returns the number of players currently registered."""
    db, cursor = connect()
    cursor.execute("SELECT COUNT(*) FROM Player")
    return cursor.fetchall()[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db, cursor = connect()
    cursor.execute("insert into Player (full_name) values (%s)", (name,))
    db.commit()


def registerTournament(description):
    """Adds a tournament to the tournament database.

    The database assigns a unique serial id number for the tournament.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      description: the tournament description
    """
    db, cursor = connect()
    query = "insert into Tournament (description) values (%s)"
    param = (description,)
    cursor.execute(query, param)
    db.commit()

    cursor.execute("SELECT MAX(id) FROM Tournament")
    return cursor.fetchall()[0][0]


def playerStandings(tournament):
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
    num_matches = {}

    db, cursor = connect()
    sql = "SELECT p.id, p.full_name, COUNT(m.id) AS matches FROM player p LEFT JOIN match m ON p.id = player1 OR p.id = player2 "
    sql += " LEFT JOIN tournament t ON m.tournament = t.id AND m.tournament = %s GROUP BY p.id"
    cursor.execute(sql, (tournament,))
    for row in cursor.fetchall():
        num_matches[row[0]] = row[2]

    sql = "SELECT p.id, p.full_name, COUNT(winner) AS wins FROM player p LEFT JOIN match m ON p.id = winner "
    sql += " LEFT JOIN tournament t ON m.tournament = t.id AND m.tournament = %s GROUP BY p.id, winner ORDER BY wins DESC"
    cursor.execute(sql, (tournament,))
    standings = [(row[0], row[1], row[2], num_matches[row[0]]) for row in cursor]
    return standings


def reportMatch(player1, player2, winner, round, tournament):
    """Report a single match between two players.

    Args:
      player1: the id number of the first player
      player2: the id number of the second player
      winner:  the id number of the player who won
      round:   the id number of the tournament round
      tournament:  the id number of the tournament
    """
    db, cursor = connect()
    sql = "INSERT INTO Match (player1, player2, winner, round, tournament) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (player1, player2, winner, round, tournament))
    db.commit()


def swissPairings(tournament):
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
    pairings = []
    standings = playerStandings(tournament)
    c = 0
    for s in standings:
        ranked_player = (s[0], s[1])

        if c % 2 == 0:
            pairings.append(ranked_player)
        else:
            curr_entry = len(pairings)-1
            pairings[curr_entry] = pairings[curr_entry] + ranked_player

        c += 1

    return pairings

