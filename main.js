import { createBoard, playMove } from "./connect4.js";

// TODO: find deployment-compatible way to read a config file
const WEBSOCKET_SERVER = 'wss://websockets-connect4.highball.org';

function getWebSocketServer() {
  // if running on localhost assume ws server is listening on port 8001
  if (window.location.host.includes("localhost")) {
    return "ws://localhost:8001/";
  } else {
    return WEBSOCKET_SERVER;
    //throw new Error(`Unsupported host: ${window.location.host}`);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  // Initialize the UI.
  const board = document.querySelector(".board");
  createBoard(board);
  // Open the WebSocket connection and register event handlers.
  const serverUrl = getWebSocketServer();
  console.log("connecting to " + serverUrl);
  const websocket = new WebSocket(serverUrl);
  initGame(websocket);
  receiveMoves(board, websocket);
  sendMoves(board, websocket);
});


function initGame(websocket) {
  websocket.addEventListener("open", () => {
    const params = new URLSearchParams(window.location.search);
    let event = { type: "init" };
    if (params.has("game_id")) {
      // Second player joins an existing game.
      event.game_id = params.get("game_id");
    }
    websocket.send(JSON.stringify(event));
  });
}


function sendMoves(board, websocket) {
  // When clicking a column, send a "play" event for a move in that column.
  board.addEventListener("click", ({ target }) => {
    const column = target.dataset.column;
    // Ignore clicks outside a column.
    if (column === undefined) {
      return;
    }
    const event = {
      type: "play",
      column: parseInt(column, 10),
    };
    websocket.send(JSON.stringify(event));
  });
}


function showMessage(message) {
  window.setTimeout(() => window.alert(message), 50);
}


function receiveMoves(board, websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "init":
        // Create link for inviting the second player.
        document.querySelector(".join").href = "?game_id=" + event.game_id;
        break;

      case "play":
        // Update the UI with the move.
        playMove(board, event.player, event.column, event.row);
        break;

      case "win":
        showMessage(`Player ${event.player} wins!`);
        // No further messages are expected; close the WebSocket connection.
        websocket.close(1000);
        break;

      case "error":
        showMessage(event.message);
        break;

      default:
        throw new Error(`Unsupported event type: ${event.type}.`);
    }
  });
}

