#coding=utf-8
__author__ = 'ron975'
"""
This file is part of Snowflake.Core
"""
import sqlite3
import os
import json

from snowflake import utils, constants
from snowflake.types import Game
#Games Database
games_db = sqlite3.connect(os.path.join(constants.directory_data, "games.db"))


def create_games_database():
    """
    Creates games database if not there
    :return:
    """
    try:
        games_db.cursor().execute("CREATE TABLE games "
                                  "(uuid TEXT, gamename TEXT, consoleid TEXT, rompath TEXT, metadata TEXT)")
        games_db.commit()
        return True
    except sqlite3.Error, e:
        utils.server_log("SQL Error Encountered, Unable to Create Database:", e.args[0])
        return False


def insert_game(game):
    """
    Adds a game to the database
    :param game:
    :return:
    """

    try:
        #Because we don't know how much metadata there will be, we use ''.join() for efficiency
        games_db.cursor().execute(''.join([
            'INSERT INTO games VALUES("{uuid}","{gamename}","{consoleid}","{rompath}","'
            .format(**game.__dict__).replace("'", "''"),
            json.dumps(game.metadata).replace('"', '""'), '")'
        ]))

        games_db.commit()
        utils.server_log("Inserted Game '{gamename}' ({rompath}) with uuid {uuid}".format(**game.__dict__))
        return True
    except sqlite3.Error, e:
        utils.server_log("SQL Error Encountered, Unable to Insert Game:", e.args[0])
        return False


def delete_game(game_id):
    #todo Test this
    try:
        cur = games_db.cursor()
        cur.execute('DELETE * FROM games WHERE uuid="{0}"'.format(game_id))
        games_db.commit()

    except sqlite3.Error, e:
        utils.server_log("SQL Error Encountered, could not delete game {0}".format(game_id))
        return None


def search_game(name="", consoleid="", metadata={}):
    """
    Searches for a game given parameters
    :param name: Title of the game to search
    :param consoleid: Console ID of the game to search
    :param metadata: Any metadata to search
    :return:
    """

    #fields
    games = []
    searchstrings = []

    #Build the SQLite statement
    if name is not "":
        searchstrings.append(''.join(['gamename LIKE "%', name, '%"']))
    if consoleid is not "":
        searchstrings.append(''.join(['consoleid = ', '"', consoleid, '"']))
    if metadata is not {}:
        for metadatakey, metadatavalue in metadata.iteritems():
            searchstrings.append(''.join(['metadata LIKE "%""', metadatakey, '"": ""', metadatavalue, '""%"']))

    #If no arguments were provided, log
    if not searchstrings:
        utils.server_log("Empty Searchstring while searching for strings")
        pass

    else:

        try:
            cur = games_db.cursor()
            #Execute the SQLite
            cur.execute('SELECT * FROM games WHERE ' + ' AND '.join(searchstrings))

            #Add all results to array
            for result in cur.fetchall():
                uuid, gamename, consoleid, rompath, metadata = result
                games.append(Game(uuid, gamename, consoleid, rompath, **json.loads(metadata)))
        #Log any errors
        except sqlite3.Error, e:
            utils.server_log("Error encountered while searching for game with name", name, "consoleid", consoleid,
                                    "metadata", str(metadata), ", ", e.args[0])
            pass

    #Return nothing, bor array of games
    return games


def get_game_by_uid(game_id):
    #todo Test this
    try:
        cur = games_db.cursor()
        cur.execute('SELECT * FROM games WHERE uuid="{0}"'.format(game_id))
        uuid, gamename, systemid, rompath, metadata = cur.fetchone()
        return Game(uuid, gamename, systemid, rompath, **json.loads(metadata))

    except sqlite3.Error, e:
        utils.server_log("SQL Error Encountered, Could not search for games")
        return None


def get_games_for_system(systemid):
    games = []
    try:
        cur = games_db.cursor()
        cur.execute('SELECT * FROM games WHERE consoleid="{0}"'.format(systemid))

        for result in cur.fetchall():
            uuid, gamename, systemid, rompath, metadata = result
            games.append(Game(uuid, gamename, systemid, rompath, **json.loads(metadata)))

    except sqlite3.Error, e:
        utils.server_log("SQL Error Encountered, Could not search for games")

    return games

