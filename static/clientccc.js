var pc = null;
var socket = new WebSocket('ws://127.0.0.1:8000/rtc/ws');

async function offer() {
    console.log("offer 함수 호출됨");

    // WebSocket 메시지 처리
    socket.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        console.log(message);

        try {
            if (message.type === 'candidate') {
                console.log("onmessage:candidate");
                await pc.addIceCandidate(new RTCIceCandidate(message.candidate));
            } else if (message.type === 'answer') {
                console.log("onmessage:answer");
                await pc.setRemoteDescription(new RTCSessionDescription(message));
            } else if (message.type === 'offer') {
                console.log("onmessage:offer");
                await pc.setRemoteDescription(new RTCSessionDescription(message));
                const answer = await pc.createAnswer();
                console.log("onmessage:createanswer");
                await pc.setLocalDescription(answer);
                socket.send(JSON.stringify({ type: 'answer', sdp: pc.localDescription.sdp }));
            }
        } catch (error) {
            console.error('Error handling message:', error);
        }
    };
}

function negotiate() {
    console.log("onmessage:negotiate");
    if (!pc) {
        console.error("RTCPeerConnection is not initialized.");
        return;
    }

    pc.addTransceiver('video', { direction: 'sendrecv' });
    pc.addTransceiver('audio', { direction: 'sendrecv' });

    return pc.createOffer()
        .then((offer) => {
            return pc.setLocalDescription(offer);
        })
        .then(() => {
            return fetch('http://70.12.247.123:8000/rtc/offer', {
                body: JSON.stringify({
                    sdp: pc.localDescription.sdp,
                    type: pc.localDescription.type,
                }),
                headers: {
                    'Content-Type': 'application/json'
                },
                method: 'POST'
            });
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((answer) => {
            return pc.setRemoteDescription(answer);
        })
        .catch((e) => {
            alert(e);
            console.error('Error in negotiation:', e);
        });
}

async function start() {
    try {
        // 웹소켓이 열리면 offer 함수를 호출
        socket.onopen = () => {
            console.log("websocket 연결됨");
            const config = {
                sdpSemantics: 'unified-plan',
                iceServers: [
                    {
                        urls: 'stun:stun.l.google.com:19302' // STUN 서버
                    },
                    {
                        urls: 'turn:j11a203.p.ssafy.io', // TURN 서버
                        username: 'username',
                        credential: 'password'
                    }
                ]
            };
            pc = new RTCPeerConnection(config); // 전역 pc 변수 사용

            pc.oniceconnectionstatechange = () => {
                console.log('ICE Connection State:', pc.iceConnectionState);
                if (pc.iceConnectionState === 'connected') {
                    console.log('Connection established!');
                }
            };

            // negotiate()를 호출하여 연결을 시작
            negotiate();
        };

        // 웹캠 및 오디오 스트림 요청
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { frameRate: 15 }, 
            audio: true 
        });
        const video = document.getElementById('video');

        // 비디오 요소에 스트림 연결
        video.srcObject = stream;

        // WebSocket이 열리기 전에 addTrack을 호출하지 않도록 수정
        socket.onopen = async () => {
            console.log("websocket 연결됨");
            const config = {
                sdpSemantics: 'unified-plan',
                iceServers: [
                    {
                        urls: 'stun:stun.l.google.com:19302' // STUN 서버
                    },
                    {
                        urls: 'turn:j11a203.p.ssafy.io', // TURN 서버
                        username: 'username',
                        credential: 'password'
                    }
                ]
            };
            pc = new RTCPeerConnection(config);

            // 스트림의 모든 트랙을 PeerConnection에 추가
            stream.getTracks().forEach(track => {
                pc.addTrack(track, stream);
            });

            negotiate(); // 연결 시작
        };

        document.getElementById('start').style.display = 'none';
        document.getElementById('stop').style.display = 'block';

    } catch (error) {
        console.error('Error accessing media devices.', error);
    }
}

function stop() {
    if (pc) {
        pc.close();
    }
    document.getElementById('start').style.display = 'block';
    document.getElementById('stop').style.display = 'none';
}
