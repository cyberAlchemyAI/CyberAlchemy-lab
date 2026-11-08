import http from "node:http";

http.createServer((_, response) => {
  response.statusCode = 204;
  response.end();
}).listen(8080);
