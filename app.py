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

        event_type = event.get("type")
        response = {
            "type": "error",
            "message": f"Unknown event type {event_type}",
        }

        if event_type == "play":
            try:
                column = event["column"]
                row = game.play(player, column)
            except (ValueError, KeyError) as exc:
                response = {
                    "type": "error",
                    "message": str(exc),
                }
                await websocket.send(json.dumps(response))
                continue

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

        await websocket.send(json.dumps(response))


async def main():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
