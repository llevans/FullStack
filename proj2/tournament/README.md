
README
======

Tournament Python module
------------------------

This application is a python module that can be used to manage a tournament.
The module functions can be used to
  1. Register a Player
  2. Register a Tournament
  3. Record the outcome of a match
  4. Retrieve player standings in a tournament
  5. Pair players for a tournament round based on Swiss pairing style
  6. Remove all players, all matches or all tournaments
  9. Remove tournament matches

To execute this module:

  Import the tournament module into your application
    'import tournament' in your python app

  Invoke the methods to manage your tournament:
    registerPlayer
    registerTournament
    deleteMatches
    deleteTourMatches
    deletePlayers
    deleteTournaments
    countPlayers
    playerStandings
    reprtMatch
    swissPairings


Testing:

   Initiate PostgreSQL database
        Create database	    - 'psql -c "drop database if exists tournament"'
                              'psql -c "create database tournament"'
   	Connect to database - 'psql tournament'
    	Add database tables - Run psql command  '\i tournament.sql'

   Execute tests:
        Run command "python tournament_test.py"



