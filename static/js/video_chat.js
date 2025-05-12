document.addEventListener('DOMContentLoaded', function () {

    let localStream = null;
    let pc = null;
    let roomId = null;
    let role = null;
    let polling = false;

    const startBtn = document.getElementById('startButton');
    const callBtn = document.getElementById('callButton');
    const joinBtn = document.getElementById('joinButton');
    const hangupBtn = document.getElementById('hangupButton');
    const localVideo = document.getElementById('localVideo');
    const remoteVideo = document.getElementById('remoteVideo');
    const roomIdInput = document.getElementById('roomId');

    startBtn.onclick = async () => {
        try {
            localStream = await navigator.mediaDevices.getUserMedia({
                audio: true,
                video: true
            });
        } catch (e) {
            // Если камера не доступна, пробуем только аудио
            try {
                localStream = await navigator.mediaDevices.getUserMedia({
                    audio: true,
                    video: false
                });
                alert("Камера не найдена или не разрешена. Используется только микрофон.");
            } catch (err) {
                alert("Нет доступа к микрофону и камере!");
                return;
            }
        }
        localVideo.srcObject = localStream;
        startBtn.disabled = true;
        callBtn.disabled = false;
        joinBtn.disabled = false;
    };

    callBtn.onclick = async () => {
        roomId = roomIdInput.value.trim();
        if (!roomId) {
            alert("Введите room_id!");
            return;
        }
        role = "offer";
        callBtn.disabled = true;
        joinBtn.disabled = true;
        hangupBtn.disabled = false;

        pc = createPeerConnection();

        localStream.getTracks().forEach(track => pc.addTrack(track, localStream));

        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        await fetch(document.location.pathname, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                room_id: roomId,
                role: "offer",
                sdp: offer.sdp,
                type: offer.type
            })
        });

        polling = true;
        pollSignals();
    };

    joinBtn.onclick = async () => {
        roomId = roomIdInput.value.trim();
        if (!roomId) {
            alert("Введите room_id!");
            return;
        }
        role = "answer";
        callBtn.disabled = true;
        joinBtn.disabled = true;
        hangupBtn.disabled = false;

        pc = createPeerConnection();
        localStream.getTracks().forEach(track => pc.addTrack(track, localStream));

        let offerData = null;
        while (!offerData) {
            const resp = await fetch(document.location.pathname, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    room_id: roomId,
                    role: "answer"
                })
            });
            const data = await resp.json();
            if (data.offer) {
                offerData = data.offer;
                break;
            }
            await new Promise(r => setTimeout(r, 1000));
        }

        await pc.setRemoteDescription(new RTCSessionDescription(offerData));

        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);

        await fetch(document.location.pathname, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                room_id: roomId,
                role: "answer",
                sdp: answer.sdp,
                type: answer.type
            })
        });

        polling = true;
        pollSignals();
    };

    hangupBtn.onclick = async () => {
        polling = false;
        if (pc) pc.close();
        pc = null;
        localVideo.srcObject = null;
        remoteVideo.srcObject = null;
        startBtn.disabled = false;
        callBtn.disabled = true;
        joinBtn.disabled = true;
        hangupBtn.disabled = true;
        if (roomId) {
            await fetch(`/close/${document.location.pathname.split('/')[2]}/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({room_id: roomId})
            });
        }
    };

    function createPeerConnection() {
        const pc = new RTCPeerConnection({
            iceServers: [{urls: 'stun:stun.l.google.com:19302'}]
        });

        pc.onicecandidate = async (event) => {
            if (event.candidate) {
                await fetch(document.location.pathname, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        room_id: roomId,
                        role: role,
                        candidate: event.candidate.candidate,
                        sdpMid: event.candidate.sdpMid,
                        sdpMLineIndex: event.candidate.sdpMLineIndex
                    })
                });
            }
        };

        pc.ontrack = (event) => {
            remoteVideo.srcObject = event.streams[0];
        };

        return pc;
    }

    async function pollSignals() {
        while (polling) {
            const resp = await fetch(document.location.pathname, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    room_id: roomId,
                    role: role
                })
            });
            const data = await resp.json();

            if (role === "offer" && data.answer && pc.signalingState !== "stable") {
                await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
            }

            if (data.candidates) {
                for (const cand of data.candidates) {
                    try {
                        await pc.addIceCandidate(cand);
                    } catch (e) {}
                }
            }
            await new Promise(r => setTimeout(r, 1000));
        }
    }
});