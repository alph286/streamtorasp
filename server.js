// server.js
const express = require("express");
const http = require("http");
const { Server } = require("ws");
const osc = require("osc");

const OSC_UDP_PORT = 8000;    // da impostare nel tuo OSC Out di TouchDesigner
const WS_PORT = 8081;         // porta WebSocket per il browser

// HTTP static (opzionale: serve la pagina client)
const app = express();
app.use(express.static("public"));
const server = http.createServer(app);
server.listen(WS_PORT, () => console.log(`WS/HTTP su :${WS_PORT}`));

// WebSocket
const wss = new Server({ server });

// OSC UDP Listener
const udpPort = new osc.UDPPort({
  localAddress: "0.0.0.0",
  localPort: OSC_UDP_PORT,
  metadata: true
});

udpPort.on("message", (oscMsg) => {
  const payload = {
    address: oscMsg.address,
    args: (oscMsg.args || []).map(a => a.value ?? a) // normalizza
  };
  // broadcast a tutti i client WebSocket
  wss.clients.forEach(c => {
    if (c.readyState === 1) c.send(JSON.stringify(payload));
  });
});

udpPort.on("ready", () => {
  console.log(`OSC in ascolto su UDP :${OSC_UDP_PORT}`);
});
udpPort.open();
