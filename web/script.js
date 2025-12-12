const startBtn = document.getElementById("startBtn");
const avatarVideo = document.getElementById("avatarVideo");

startBtn.onclick = async () => {
    const tokenResp = await fetch("https://YOUR-RAILWAY-URL/token");
    const { token, url } = await tokenResp.json();

    const room = await LiveKit.connect(url, token);

    room.on("trackSubscribed", (track, publication, participant) => {
        if (track.kind === "video") {
            avatarVideo.srcObject = new MediaStream([track.mediaStreamTrack]);
        }
    });
};
