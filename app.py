#!/usr/bin/env python3

import asyncio
import json
import logging

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK

from connect4 import PLAYER1, PLAYER2, Connect4


logging.basicConfig(format="%(message)s", level=logging.DEBUG)


async def handler(websocket):
    game = Connect4()
    move = 0
    players = [PLAYER1, PLAYER2]

    async for message in websocket:
        logging.debug(message)
        event = json.loads(message)
        logging.debug(event)
        # handle play events, alternating between users
        move = move + 1
        player = players[move % 2]

        response = {}
        if event.get("type") == "play":
            column = event.get("column")
            try:
                row = game.play(player, column)

                if game.last_player_won:
                    response = {
                        "type": "win",
                        "player": player,
                    }
                else:
                    response = {
                        "type": "play",
                        "player": player,
                        "column": column,
                        "row": row,
                    }

            except ValueError as exc:
                response = {
                    "type": "error",
                    "message": str(exc),
                }

        await websocket.send(json.dumps(event))


async def handler(websocket):
    for player, column, row in [
        (PLAYER1, 3, 0),
        (PLAYER2, 3, 1),
        (PLAYER1, 4, 0),
        (PLAYER2, 4, 1),
        (PLAYER1, 2, 0),
        (PLAYER2, 1, 0),
        (PLAYER1, 5, 0),
    ]:
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        await websocket.send(json.dumps(event))
        await asyncio.sleep(0.5)

    event = {
        "type": "win",
        "player": PLAYER1,
    }
    await websocket.send(json.dumps(event))


async def main():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
