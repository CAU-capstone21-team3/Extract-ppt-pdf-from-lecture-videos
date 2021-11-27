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
  response.sendFile(__dirname + '/home.html');
})

pre_app.get('/stu', (request, response) => {
  response.sendFile(__dirname + '/stud_index.html');
})

pre_app.get('/prof', (request, response) => {
  response.sendFile(__dirname + '/prof_index.html');
})
pre_app.get('/pdf', (request, response) => {
  response.sendFile("C:\\waste\\a4.pdf");
})

//io.to(studentIp).sendFile("C:\\waste\\a4.pdf");

let socketId1;
let socketId2;
let studentId;
let people = 0;
io.sockets.on('connection', function (socket) {
  if (people == 0) {
    socketId1 = socket.id;
    people = 1;
  } else {
    socketId2 = socket.id;
  }
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
  //student 시작점 . 
  socket.on('join', function (room) {
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
  ///////////////////////////////////////////////////////////////
  const doc = new jsPDF();
  ///////////////////////////////////////////////////////////////
  socket.on('recordStop', () => {
    console.log("저장 변환...!!!");
    doc.save("C:\\waste\\a4.pdf");
    io.to(socketId1).emit('redirect', "http://localhost:8000/pdf");
    io.to(socketId2).emit('redirect', "http://localhost:8000/pdf");
  })
  //////////////////////////////////////////////////////////////////
  ///////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////
  let frame_array = [];
  let origin_slide_array = [];
  let slide_num = 0;
  let current_frame_index = 0;

  let prev_frame;

  let first = 1;

  let width = 1280;
  let height = 720;
  /////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////
  function detect_difference(before_frame, after_frame) {

    let cal_mat = after_frame.absdiff(before_frame);
    let sqrt_cal_mat = cal_mat.hMul(cal_mat);
    let sqrt_cal_vec = sqrt_cal_mat.sum();
    let diff = sqrt_cal_vec.x + sqrt_cal_vec.y + sqrt_cal_vec.z;
    diff = diff / (width * height);
    console.log(diff);
    return diff;
  }

  function detect_different_part(before_frame, after_frame) {

    let before = new cv.Mat(720, 1280, cv.CV_8UC4);
    let after = new cv.Mat(720, 1280, cv.CV_8UC4);
    before = before_frame;
    after = after_frame;

    let slice = 4;
    let different_slice = 0;
    let temp_image1 = new cv.Mat();
    let temp_image2 = new cv.Mat();

    let slice_height = parseInt(height / slice);
    let slice_width = parseInt(width / slice);

    for (let i = 0; i < slice; i++) {
      for (let j = 0; j < slice; j++) {
        temp_image1 = before.getRegion(new cv.Rect(slice_width * i, slice_height * j, slice_width, slice_height));
        temp_image2 = after.getRegion(new cv.Rect(slice_width * i, slice_height * j, slice_width, slice_height));
        if (detect_difference(temp_image1, temp_image2) > 5) {
          different_slice += 1;
        }
      }
    }
    return different_slice;
  }

  let state = 1;

  /////////////////////////////////////////////////////////
  socket.on('pdf', (send_image) => {
    var dataUrlRegExp = /^data:image\/\w+;base64,/;
    var base64Data = send_image.replace(dataUrlRegExp, "");
    //var imageBuffer = new Buffer.alloc(base64Data, "base64");
    let decode = Buffer.from(base64Data, 'base64');

    //파일 안깨지는건 확인 하였음 ....
    fs.writeFileSync("C:\\waste\\result.png", decode);

    let temp_frame = new cv.Mat(height, width, cv.CV_8UC4);
    temp_frame = cv.imdecode(decode);
    //////////////////////////////////////////////
    //////////////////////////////////////////////
    if (first == 1) {
      first = 0;
      //doc.text("hello world", 10, 10);
      //doc.addImage(send_image, "JPEG", 15, 40, 180, 160);
      //doc.output('datauri'); <- 주석 지우지 마세요. 지우면 오류 뜹니다
      prev_frame = temp_frame;
      origin_slide_array.push(temp_frame);
      //doc.save("C:\\waste\\a4.pdf");
    } else {

      if (detect_different_part(origin_slide_array[current_frame_index], temp_frame) >= 6) {
        let exist = [false, false];
        let index = [0, 0];

        console.log("inside of if");

        for (let i = 0; i < origin_slide_array.length; i++) {
          if (detect_difference(origin_slide_array[i], temp_frame) < 5) {
            exist[0] = true;
            index[0] = i;
          }
        }

        for (let i = 0; i < frame_array.length; i++) {
          if (detect_difference(frame_array[i][0], temp_frame) < 5) {
            exist[1] = true;
            index[1] = frame_array[i][1];
          }
        }

        let prev_exist = false;

        for (let i = 0; i < frame_array.length; i++) {
          if (detect_difference(frame_array[i][0], prev_frame) < 5) {
            prev_exist = true;
            break;
          }
        }

        if ((!prev_exist) && detect_different_part(prev_frame, temp_frame) >= 4) {
          console.log("add_image");
          frame_array.push([prev_frame, current_frame_index]);

          if (state == 1) {
            doc.addImage(send_image, "JPEG", 10, 30, 190, 106);
            state = 2;
          } else if (state == 2) {
            doc.addImage(send_image, "JPEG", 10, 160, 190, 106);
            state = 3;
          } else if (state == 3) {
            doc.addPage();
            doc.addImage(send_image, "JPEG", 10, 30, 190, 106);
            state = 2;
          }
        }

        if (!exist[0] && !exist[1]) {
          console.log("여기 들어오나요 ? slid _ num ++");
          console.log(slide_num);

          origin_slide_array.push(temp_frame);
          slide_num += 1;
          current_frame_index = slide_num;
        } else if (exist[0] && !exist[1]) {
          current_frame_index = index[0];
        } else if (!exist[0] && exist[1]) {
          current_frame_index = index[1];
        }

        prev_frame = temp_frame;

      }
    }
    //잘 출력되는 거 확인 하였음 ...
    //cv.imshowWait('Image', temp_frame);

    //temp_frame 이 cv.mat <- 이거로 연산 해야 합니다 . 
  })

});
