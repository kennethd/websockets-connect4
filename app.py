#!/usr/bin/env python3

import asyncio
import itertools
import json
import logging
import os
import secrets
import signal

from websockets.asyncio.client import connect
from websockets.asyncio.server import broadcast, serve
from websockets.exceptions import ConnectionClosedOK

from connect4 import PLAYER1, PLAYER2, Connect4


logging.basicConfig(format="%(message)s", level=logging.DEBUG)

# global dict to manage connections for players connected to a game;
# keyed on game_id, values are sets of websocket connections
PLAYERS = {}
# second global dict for non-players who are watching the game;
# keyed on game_id, values are sets of websocket connections
WATCHERS = {}
# limit number of allowed games
MAX_GAMES = 24


def reset_global_state():
    """reset global state for doctests"""
    # since global state is temporary kludge, just reset it between tests
    global PLAYERS, WATCHERS, MAX_GAMES
    PLAYERS = {}
    WATCHERS = {}
    MAX_GAMES = 24


def lookup_game(game_id):
    """retrieve game instance and set of connections for game_id

    raises RuntimeError if game is not found

    >>> reset_global_state()
    >>> websocket = connect("ws://localhost:0")
    >>> game_id = create_game(websocket)
    >>> game, connections = lookup_game(game_id)
    >>> assert game
    >>> assert len(connections) == 1
    >>> destroy_game(game_id)
    >>> game, connections = lookup_game(game_id)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    RuntimeError: Game not found: '...'
    """
    logging.debug(f"lookup game {game_id}")
    try:
        game, connections = PLAYERS[game_id]
        logging.debug(f"found game {game_id} with conns {connections}")
    except KeyError:
        raise RuntimeError(f"Game not found: '{game_id}'")
    return game, connections


def create_game(websocket):
    """Initialize a new game

    raises RuntimeError if > MAX_GAMES in progress

    >>> reset_global_state()
    >>> websocket = connect("ws://localhost:0")
    >>> game_id = create_game(websocket)
    >>> game, conns = lookup_game(game_id)
    >>> assert game
    >>> assert len(conns) == 1
    >>> assert websocket in conns
    >>> game, conns = game_watchers(game_id)
    >>> assert len(conns) == 0
    >>> game_ids = []
    >>> for i in range(MAX_GAMES):
    ...     game_ids.append(create_game(websocket))
    >>> game_id = create_game(websocket)
    Traceback (most recent call last):
    ...
    RuntimeError: too many active games
    """
    if len(PLAYERS) > MAX_GAMES:
        raise RuntimeError("too many active games")

    game = Connect4()
    game_id = secrets.token_urlsafe(12)
    if game_id in PLAYERS.keys():
        raise RuntimeError(f"already have a game with id {game_id}")

    # connections is set of ws conns to be notified of state changes
    connections = {websocket}
    PLAYERS[game_id] = game, connections
    WATCHERS[game_id] = game, set()
    return game_id


def destroy_game(game_id):
    """remove game from in-progress games

    >>> reset_global_state()
    >>> websocket = connect("ws://localhost:0")
    >>> game_id = create_game(websocket)
    >>> game, conns = lookup_game(game_id)
    >>> assert game
    >>> assert len(conns) == 1
    >>> assert websocket in conns
    >>> game, conns = game_watchers(game_id)
    >>> assert len(conns) == 0
    >>> destroy_game(game_id)
    >>> game, conns = lookup_game(game_id)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    RuntimeError: Game not found: '...'
    """
    logging.debug(f"destroy game {game_id}")
    try:
        del PLAYERS[game_id]
        del WATCHERS[game_id]
    except KeyError:
        logging.debug(f"no {game_id} in {PLAYERS.keys()}")
        pass


def leave_game(websocket, game_id):
    # i'm really not sure this is necessary given the behavior of destroy_game
    game, connections = lookup_game(game_id)
    try:
        connections.remove(websocket)
    except KeyError:
        logging.debug(f"current websocket not found in game {game_id}")
        pass


def watch_game(websocket, game_id):
    try:
        game, connections = WATCHERS[game_id]
        connections.add(websocket)
    except KeyError:
        logging.debug(f"current websocket not found in game {game_id}")
        pass


def unwatch_game(websocket, game_id):
    try:
        game, connections = WATCHERS[game_id]
        connections.remove(websocket)
    except KeyError:
        logging.debug(f"current websocket not found in game {game_id}")
        pass


def game_watchers(game_id):
    try:
        game, connections = WATCHERS[game_id]
    except KeyError:
        logging.debug(f"{game_id} found in watchers list")
        pass
    return game, connections


async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def init_game(websocket):
    """called when player creates a new game

    player automatically becomes PLAYER1"""
    game_id = create_game(websocket)
    # send game_id back to client, so first player can invite others
    event = {
        "type": "init",
        "game_id": game_id,
    }
    await websocket.send(json.dumps(event))

    try:
        # enter gameplay loop
        await play(websocket, game_id, PLAYER1)
    finally:
        logging.debug(f"Game over")
        destroy_game(game_id)


async def join_game(websocket, game_id):
    """called when second player joins game at invitation of PLAYER1

    player automatically becomes PLAYER2
    """
    logging.debug(f"join game {game_id}")
    game, connections = lookup_game(game_id)
    connections.add(websocket)

    try:
        # enter gameplay loop
        await play(websocket, game_id, PLAYER2)
    finally:
        logging.debug(f"{PLAYER2} leaving game {game_id}")
        leave_game(websocket, game_id)


async def play(websocket, game_id, player):
    """gameplay loop"""
    game, connections = lookup_game(game_id)

    # TODO: Wait for player2 to join
    # TODO: Add event to notify player it's their turn
    # TODO: Add timeout to destroy idle games

    async for message in websocket:
        logging.debug(message)
        event = json.loads(message)
        logging.debug(event)
        # once a game is started/joined only valid client event is play
        assert event.get("type") == "play"

        try:
            column = event["column"]
            logging.debug(f"player {player} plays col {column}")
            row = game.play(player, column)
        except (ValueError, KeyError) as exc:
            await error(websocket, str(exc))
            continue

        play_event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        broadcast(connections, json.dumps(play_event))

        if game.last_player_won:
            win_event = {
                "type": "win",
                "player": player,
            }
            broadcast(connections, json.dumps(win_event))


async def handler(websocket):
    # handler accepts init, join or watch events, then delegates to event loop;
    # therefore we only need .recv() one message
    message = await websocket.recv()
    logging.debug(message)
    event = json.loads(message)
    logging.debug(event)

    event_type = event.get("type")

    if event_type == "init":
        game_id = event.get("game_id")
        if not game_id:
            await init_game(websocket)
        else:
            await join_game(websocket, game_id)
    else:
        await error(websocket, f"Unknown event type {event_type}")


async def main():
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", "8001"))
    async with serve(handler, "", port):
        await stop


if __name__ == "__main__":
    asyncio.run(main())

