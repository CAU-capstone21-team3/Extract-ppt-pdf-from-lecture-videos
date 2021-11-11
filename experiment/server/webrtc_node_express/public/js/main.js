'use strict';

document.write("<script src='https://docs.opencv.org/3.3.1/opencv.js'></<script>");
//const cv = require('opencv4nodejs');
//const image = cv.imread('image/test.png');
//cv.imshowWait('Image', image);

var isChannelReady = false;
var isInitiator = false;
var isStarted = false;
var localStream;
var pc;
var remoteStream;
var turnReady;

var pcConfig = {
  'iceServers': [{
    'urls': 'stun:stun.l.google.com:19302'
  }]
};

// Set up audio and video regardless of what devices are present.
var sdpConstraints = {
  offerToReceiveAudio: true,
  offerToReceiveVideo: true
};

/////////////////////////////////////////////

var room = 'foo';
// Could prompt for room name:
// room = prompt('Enter room name:');

var socket = io.connect();

if (room !== '') {
  socket.emit('create or join', room);
  console.log('Attempted to create or  join room', room);
}

socket.on('created', function (room) {
  console.log('Created room ' + room);
  isInitiator = true;
});

socket.on('full', function (room) {
  console.log('Room ' + room + ' is full');
});

socket.on('join', function (room) {
  console.log('Another peer made a request to join room ' + room);
  console.log('This peer is the initiator of room ' + room + '!');
  isChannelReady = true;
});

socket.on('joined', function (room) {
  console.log('joined: ' + room);
  isChannelReady = true;
});

socket.on('log', function (array) {
  console.log.apply(console, array);
});

////////////////////////////////////////////////

function sendMessage(message) {
  console.log('Client sending message: ', message);
  socket.emit('message', message);
}

// This client receives a message
socket.on('message', function (message) {
  console.log('Client received message:', message);
  if (message === 'got user media') {
    maybeStart();
  } else if (message.type === 'offer') {
    if (!isInitiator && !isStarted) {
      maybeStart();
    }
    pc.setRemoteDescription(new RTCSessionDescription(message));
    doAnswer();
  } else if (message.type === 'answer' && isStarted) {
    pc.setRemoteDescription(new RTCSessionDescription(message));
  } else if (message.type === 'candidate' && isStarted) {
    var candidate = new RTCIceCandidate({
      sdpMLineIndex: message.label,
      candidate: message.candidate
    });
    pc.addIceCandidate(candidate);
  } else if (message === 'bye' && isStarted) {
    handleRemoteHangup();
  }
});

////////////////////////////////////////////////////

var localVideo = document.querySelector('#localVideo');
var $remoteVideo = document.querySelector('#remoteVideo');

navigator.mediaDevices.getDisplayMedia({
  audio: false,
  video: true
})
  .then(gotStream)
  .catch(function (e) {
    alert('getUserMedia() error: ' + e.name);
  });

function gotStream(stream) {
  console.log('Adding local stream.');
  localStream = stream;
  localVideo.srcObject = stream;
  sendMessage('got user media');
  if (isInitiator) {
    maybeStart();
  }
}

var constraints = {
  video: true
};

console.log('Getting user media with constraints', constraints);

if (location.hostname !== 'localhost') {
  requestTurn(
    'https://computeengineondemand.appspot.com/turn?username=41784574&key=4080218913'
  );
}

function maybeStart() {
  console.log('>>>>>>> maybeStart() ', isStarted, localStream, isChannelReady);
  if (!isStarted && typeof localStream !== 'undefined' && isChannelReady) {
    console.log('>>>>>> creating peer connection');
    createPeerConnection();
    pc.addStream(localStream);
    isStarted = true;
    console.log('isInitiator', isInitiator);
    if (isInitiator) {
      doCall();
    }
  }
}

window.onbeforeunload = function () {
  sendMessage('bye');
};

/////////////////////////////////////////////////////////

function createPeerConnection() {
  try {
    pc = new RTCPeerConnection(null);
    pc.onicecandidate = handleIceCandidate;
    pc.onaddstream = handleRemoteStreamAdded;
    pc.onremovestream = handleRemoteStreamRemoved;
    console.log('Created RTCPeerConnnection');


  } catch (e) {
    console.log('Failed to create PeerConnection, exception: ' + e.message);
    alert('Cannot create RTCPeerConnection object.');
    return;
  }
}

//const $video = document.getElementById('video');
const $canvas = document.getElementById('canvas');

//////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// opencv python --> js ////////////////////////////////////////
/////////////////////////process함수가 opencv 처리하는 함수입니다./////////////////////////////////////
////////////////////////////// =process 안에서 처리해야합니다////////////////////////////////////////////
let cap;
let src;
let dst;


let frame_array = [];
let origin_slide_array = [];
let final_slide_array = [];

let temp_diff_list = [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]];

let prev_frame;

// 선언부 new~ 지우면 복사가 안됩니다.
let temp_origin_frame = new cv.Mat(document.querySelector('#remoteVideo').height, document.querySelector('#remoteVideo').width, cv.CV_8UC4);
let temp_write_frame = new cv.Mat(document.querySelector('#remoteVideo').height, document.querySelector('#remoteVideo').width, cv.CV_8UC4);

let write_frame;

let first = 1;
let count = 0;
let width = 320;
let height = 240;
let layers;

let slice = 4;
let total_count = 0;

function process() {
  cap.read(src);

  if (first == 1) {
    //첫번째 프레임
    first = 0;

    let temp_push_frame = new cv.Mat(document.querySelector('#remoteVideo').height, document.querySelector('#remoteVideo').width, cv.CV_8UC4);
    temp_push_frame = src.clone();
    origin_slide_array.push(temp_push_frame);
    frame_array.push(temp_push_frame);
    //cv.imshow('canvas', temp_push_frame);


    /*저장 (정식)
    const context = $canvas.getContext('2d');
    context.drawImage($remoteVideo, 0, 0, width, height);
    let imageData = $canvas.toDataURL('image/png');

    const $images = document.querySelector('#images');
    const $img = document.createElement('img');
    const $a = document.createElement('a');
    const fileName = 'result_${new Date().getTime()}';

    $img.src = imageData;
    $a.href = imageData;
    $a.download = fileName;
    $a.appendChild($img);

    $images.insertBefore($a, $images.childNodes[0]);
    */

    //순간 저장.
    /*let image = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream");
    var x = window.open("Popup", "height=1,weight=1,status=no,toolbar=no,menubar=no,location=no, top =100000, left =100000");
    x.location.href = image;*/
    temp_origin_frame = src.clone();
    temp_write_frame = src.clone();
    console.log(src);
    console.log(temp_write_frame);

  } else {
    if (count < 100) {
      count += 1;
      //do nothing.
    } else {
      count = 0;
      total_count += 1;
      ////
      const context = $canvas.getContext('2d');
      context.drawImage($remoteVideo, 0, 0, width, height);
      let imageData = $canvas.toDataURL('image/png');

      const $images = document.querySelector('#images');
      const $img = document.createElement('img');
      const $a = document.createElement('a');
      const fileName = 'result_' + total_count + '.png';

      $img.src = imageData;
      $a.href = imageData;
      $a.download = fileName;
      $a.appendChild($img);

      $images.insertBefore($a, $images.childNodes[0]);
      //
      let diff_list = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
      let slice_width = width / 4;
      let slice_height = height / 4;

      let different_slide = 0;

      for (let i = 0; i < slice; i++) {
        for (let j = 0; j < slice; j++) {
          //시작점, 끝점 기록
          let start_width = slice_width * i;
          let start_height = slice_height * j;
          let end_width = slice_width * (i + 1);
          let end_height = slice_height * (j + 1);

          let temp_image1 = []
          let temp_image2 = [];
          /*
                    //이미지 자르기.
                    for (let k = 0; k < height; k++) {
                      let one_row = temp_origin_frame[k].clone();
                      let slice_one_row = one_row.slice(start_width, end_width);
                      temp_image1.push(slice_one_row);
                    }
          
                    //이미지 자르기2.
                    for (let k = 0; k < height; k++) {
                      let one_row = frame[k].clone();
                      console.log(one_row);
                      let slice_one_row = one_row.slice(start_width, end_width);
                      temp_image2.push(slice_one_row);
          
                    }
          */

        }
      }


    }

  }


  //cv.cvtColor(src, dst, cv.COLOR_RGBA2GRAY);
  //cv.imshow('canvas', dst);
  setTimeout(process, 33);
}

//////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// opencv python --> js ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////

function handleIceCandidate(event) {
  console.log('icecandidate event: ', event);
  if (event.candidate) {
    sendMessage({
      type: 'candidate',
      label: event.candidate.sdpMLineIndex,
      id: event.candidate.sdpMid,
      candidate: event.candidate.candidate
    });
  } else {
    console.log('End of candidates.');
    //remoteVideo.height = remoteVideo.videoHeight;
    //remoteVideo.width = remoteVideo.videoWidth;
    cap = new cv.VideoCapture('remoteVideo');
    src = new cv.Mat(document.querySelector('#remoteVideo').height, document.querySelector('#remoteVideo').width, cv.CV_8UC4);
    dst = new cv.Mat(document.querySelector('#remoteVideo').height, document.querySelector('#remoteVideo').width, cv.CV_8UC1);
    setTimeout(process, 33);

  }
}

function handleCreateOfferError(event) {
  console.log('createOffer() error: ', event);
}

function doCall() {
  console.log('Sending offer to peer');
  pc.createOffer(setLocalAndSendMessage, handleCreateOfferError);
}

function doAnswer() {
  console.log('Sending answer to peer.');
  pc.createAnswer().then(
    setLocalAndSendMessage,
    onCreateSessionDescriptionError
  );
}

function setLocalAndSendMessage(sessionDescription) {
  pc.setLocalDescription(sessionDescription);
  console.log('setLocalAndSendMessage sending message', sessionDescription);
  sendMessage(sessionDescription);
}

function onCreateSessionDescriptionError(error) {
  trace('Failed to create session description: ' + error.toString());
}

function requestTurn(turnURL) {
  var turnExists = false;
  for (var i in pcConfig.iceServers) {
    if (pcConfig.iceServers[i].urls.substr(0, 5) === 'turn:') {
      turnExists = true;
      turnReady = true;
      break;
    }
  }
  if (!turnExists) {
    console.log('Getting TURN server from ', turnURL);
    // No TURN server. Get one from computeengineondemand.appspot.com:
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
        var turnServer = JSON.parse(xhr.responseText);
        console.log('Got TURN server: ', turnServer);
        pcConfig.iceServers.push({
          'urls': 'turn:' + turnServer.username + '@' + turnServer.turn,
          'credential': turnServer.password
        });
        turnReady = true;
      }
    };
    xhr.open('GET', turnURL, true);
    xhr.send();
  }
}


function handleRemoteStreamAdded(event) {
  console.log('Remote stream added.');
  remoteStream = event.stream;
  remoteVideo.srcObject = remoteStream;
}

function handleRemoteStreamRemoved(event) {
  console.log('Remote stream removed. Event: ', event);
}

function hangup() {
  console.log('Hanging up.');
  stop();
  sendMessage('bye');
}

function handleRemoteHangup() {
  console.log('Session terminated.');
  stop();
  isInitiator = false;

}

function stop() {
  isStarted = false;
  pc.close();
  pc = null;
}