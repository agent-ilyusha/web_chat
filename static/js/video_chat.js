        let pc = null;
        let localStream = null;
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        const startButton = document.getElementById('startButton');
        const callButton = document.getElementById('callButton');
        const hangupButton = document.getElementById('hangupButton');

        // Конфигурация ICE серверов
        const configuration = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' }
            ]
        };

        startButton.onclick = async () => {
            try {
                localStream = await navigator.mediaDevices.getUserMedia({
                    audio: true,
                    video: true
                });
                localVideo.srcObject = localStream;
                startButton.disabled = true;
                callButton.disabled = false;
            } catch (e) {
                console.error('Ошибка доступа к медиа устройствам:', e);
            }
        };

        callButton.onclick = async () => {
            try {
                callButton.disabled = true;
                hangupButton.disabled = false;

                pc = new RTCPeerConnection(configuration);

                // Добавляем локальные треки в peer connection
                localStream.getTracks().forEach(track => {
                    pc.addTrack(track, localStream);
                });

                // Обработка входящих треков
                pc.ontrack = event => {
                    remoteVideo.srcObject = event.streams[0];
                };

                // Создаем и отправляем offer
                const offer = await pc.createOffer();
                await pc.setLocalDescription(offer);
                let url = document.location.pathname;
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        sdp: pc.localDescription.sdp,
                        type: pc.localDescription.type
                    })
                });

                const answer = await response.json();
                await pc.setRemoteDescription(new RTCSessionDescription(answer));

            } catch (e) {
                console.error('Ошибка при установке соединения:', e);
            }
        };

        hangupButton.onclick = async () => {
            if (pc) {
                pc.close();
                pc = null;
            }
            
            if (localStream) {
                localStream.getTracks().forEach(track => track.stop());
                localStream = null;
            }

            localVideo.srcObject = null;
            remoteVideo.srcObject = null;
            
            startButton.disabled = false;
            callButton.disabled = true;
            hangupButton.disabled = true;

            try {
                let url = `/close/${document.location.pathname.split('/')[2]}/`;
                await fetch(url, {
                    method: 'POST'
                });
            } catch (e) {
                console.error('Ошибка при закрытии соединения:', e);
            }
        };

        // Обработка ошибок и закрытия соединения
        window.onbeforeunload = () => {
            if (pc) {
                pc.close();
            }
        };