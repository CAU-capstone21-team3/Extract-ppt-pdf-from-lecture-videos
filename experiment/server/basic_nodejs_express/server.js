const cv = require('opencv4nodejs');
var http = require('http');
const fs = require('fs');
var static = require('node-static');
const express = require('express');
const app = express();

app.use(express.static('public'));


app.get('', (request, response) => {
    response.sendFile(__dirname + '/teacher.html');
})

app.listen(8000, '127.0.0.1', () => {
    console.log("listening on port 8000");
})


/*
var server = http.createServer(function (request, response) {
    //어떻게 응답(동작) 할지 서술하는 공간.

    console.log('Client connection');

    response.writeHead(200, { 'Content-Type': 'text/html' });
    file.serve(request, response);
    fs.readFile('./teacher.html', (err, data) => {
        if (err) {
            return console.error(err);
        }
        response.end(data, 'utf-8');
    });
});

server.on('error', (err) => {
    console.log(err);
});

server.listen(8000, '127.0.0.1', () => {
    console.log('listen', server.address());
});
//const image = cv.imread('./test.png');
//cv.imshowWait('Image', image);
*/