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

  ///////////////// variables

  let first = 1;

  let frame_array_index = [];
  let frame_array = [];
  let origin_slide_array = [];
  let slide_num = 0;
  let current_frame_index= 0;

  let prev_frame;

  const doc = new jsPDF();
  
  ///////////////// functions

  function detect_difference(before_frame, after_frame){
    let error = 0;
    let row = 240;
    let col = 320;
    let bf_pixel; // before_frame pixel
    let af_pixel; // after_frame pixel
  
    for (let i = 0; i < row; i++) {
      for (let j = 0; j < col; j++) {
        bf_pixel = before_frame.charPtr(i,j);
        af_pixel = after_frame.charPtr(i,j);
        for(let c = 0; c < 4; c++){ // color
          error += (bf_pixel[c] - af_pixel[c])**2;
        }
      }
    }
    error /= row * col;
    return error;
  }
  
  function detect_different_part(before_frame, after_frame){
    let height = 240;
    let width = 320;
    let slice = 4;
    let different_slice = 0;
    let temp_image1 = new cv.Mat();
    let temp_image2 = new cv.Mat();
  
    let slice_height = parseInt(height/slice);
    let slice_width = parseInt(width/slice);
    
    for(let i=0;i<slice;i++){
      for(let j=0;j<slice;j++){
        let rect = new cv.Rect(slice_width * i, slice_height * j, slice_width, slice_height);
        temp_image1 = before_frame.roi(rect);
        temp_image2 = after_frame.roi(rect);
        if(detect_difference(temp_image1, temp_image2) > 4000){
          different_slice+=1;
        }
  
      }
    }
    temp_image1.delete();
    temp_image2.delete();
  
    return different_slice;
  }

  ////////

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

      //doc.text("hello world", 10, 10);
      doc.addImage(send_image, "JPEG", 15, 40, 180, 160);
      //doc.output('datauri'); <- 주석 지우지 마세요. 지우면 오류 뜹니다

      doc.save("C:\\waste\\a4.pdf");
      first = 0;

      prev_frame = temp_frame;
      origin_slide_array.push(temp_frame);
      frame_array.push(temp_frame);
      frame_array_index.push(0);
      slide_num +=1;
    }
    else{
      if (detect_different_part(origin_slide_array[current_frame_index], temp_frame) >=6){
        let exist = [false, false];
        let index = [0,0];
        for (let i=0; i<origin_slide_array.length; i++){
          if(detect_difference(origin_slide_array[i], frame) < 50){
            exist[0] = true;
            index[0] = i;
          }
        }
        for (let i=0; i<frame_array.length; i++){
          if(detect_difference(frame_array[i], frame) < 50){
            exist[1] = true;
            index[1] = frame_array_index[i];
          }
        }

        if (!exist[0] && !exist[1]){
          doc.addImage(send_image, "JPEG", 15, 40, 180, 160);
          origin_slide_array.push(temp_frame);
          slide_num +=1
          current_frame_index = slide_num;
        }
        else if (exist[0]&& !exist[1]){
          current_frame_index = index[0];
        }
        else if (!exist[0] && exist[1]){
          current_frame_index= index[1];
        }
        let prev_exist = false;
        
        for(let i=0;i<frame_array.length; i++){
          if(detect_difference(frame_array[i], prev_frame) <50){
            prev_exist = true;
          }
        }

        if (!prev_exist){
          frame_array.push(prev_frame);
          frame_array_index.push(current_frame_index);
        }
      }
      prev_frame = temp_frame;
    }




    //잘 출력되는 거 확인 하였음 ...
    //cv.imshowWait('Image', temp_frame);



    //temp_frame 이 cv.mat <- 이거로 연산 해야 합니다 . 
  })

});
