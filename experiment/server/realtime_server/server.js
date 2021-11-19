'use strict';

const cv = require('opencv4nodejs');
const tensor = require('@tensorflow/tfjs');
const fs = require('fs');
const { jsPDF } = require('jspdf');


var os = require('os');
var nodeStatic = require('node-static');
var http = require('http');
var express = require('express');
const pre_app = express();

pre_app.use(express.static('./public'));

var server = require('http').createServer(pre_app);
var io = require('socket.io')(server);

server.listen(8000, '127.0.0.1', () => {
  console.log("listening on port 8000");
})

pre_app.get('', (request, response) => {
  response.sendFile(__dirname + '/stud_index.html');
})

pre_app.get('/prof', (request, response) => {
  response.sendFile(__dirname + '/prof_index.html');
})
pre_app.get('/pdf', (request, response) => {
  response.sendFile("C:\\waste\\a4.pdf");
})
//io.to(studentIp).sendFile("C:\\waste\\a4.pdf");


io.sockets.on('connection', function (socket) {

  // convenience function to log server messages on the client
  function log() {
    var array = ['Message from server:'];
    array.push.apply(array, arguments);
    socket.emit('log', array);
  }

  socket.on('message', function (message) {
    log('Client said: ', message);
    // for a real app, would be room-only (not broadcast)
    socket.broadcast.emit('message', message);
  });

  //prof 시작점 .
  socket.on('create', function (room) {
    log('Received request to create or join room ' + room);

    var clientsInRoom = io.sockets.adapter.rooms[room];
    var numClients = clientsInRoom ? Object.keys(clientsInRoom.sockets).length : 0;
    log('Room ' + room + ' now has ' + numClients + ' client(s)');

    if (numClients === 0) {
      socket.join(room);
      log('Client ID ' + socket.id + ' created room ' + room);
      socket.emit('created', room, socket.id);

    } else if (numClients === 1) {
      log('Client ID ' + socket.id + ' joined room ' + room);
      io.sockets.in(room).emit('join', room);
      socket.join(room);
      socket.emit('joined', room, socket.id);
      io.sockets.in(room).emit('ready');
    } else { // max two clients
      socket.emit('full', room);
    }
  });
  let studentIp;
  //student 시작점 . 
  socket.on('join', function (room) {
    studentIp = socket.request.connection.remoteAddress;
    log('Received request to create or join room ' + room);

    var clientsInRoom = io.sockets.adapter.rooms[room];
    var numClients = clientsInRoom ? Object.keys(clientsInRoom.sockets).length : 0;
    log('Room ' + room + ' now has ' + numClients + ' client(s)');

    if (numClients === 0) {
      socket.join(room);
      log('Client ID ' + socket.id + ' created room ' + room);
      socket.emit('created', room, socket.id);

    } else if (numClients === 1) {
      log('Client ID ' + socket.id + ' joined room ' + room);
      io.sockets.in(room).emit('join', room);
      socket.join(room);
      socket.emit('joined', room, socket.id);
      io.sockets.in(room).emit('ready');
    } else { // max two clients
      socket.emit('full', room);
    }
  });
  socket.on('ipaddr', function () {
    var ifaces = os.networkInterfaces();
    for (var dev in ifaces) {
      ifaces[dev].forEach(function (details) {
        if (details.family === 'IPv4' && details.address !== '127.0.0.1') {
          socket.emit('ipaddr', details.address);
        }
      });
    }
  });

  socket.on('bye', function () {
    console.log('received bye');
  });


  let first = 1;
  socket.on('pdf', (send_image) => {
    var dataUrlRegExp = /^data:image\/\w+;base64,/;
    var base64Data = send_image.replace(dataUrlRegExp, "");
    //var imageBuffer = new Buffer.alloc(base64Data, "base64");
    let decode = Buffer.from(base64Data, 'base64');

    //파일 안깨지는건 확인 하였음 ....
    fs.writeFileSync("C:\\waste\\result.png", decode);

    let temp_frame = new cv.Mat(240, 320, cv.CV_8UC4);
    temp_frame = cv.imdecode(decode);
    console.log(temp_frame);

    if (first == 1) {
      const doc = new jsPDF();
      //doc.text("hello world", 10, 10);
      doc.addImage(send_image, "JPEG", 15, 40, 180, 160);
      //doc.output('datauri'); <- 주석 지우지 마세요. 지우면 오류 뜹니다

      doc.save("C:\\waste\\a4.pdf");
      first = 0;
    }
    //잘 출력되는 거 확인 하였음 ...
    //cv.imshowWait('Image', temp_frame);

    //temp_frame 이 cv.mat <- 이거로 연산 해야 합니다 . 
  })

});
