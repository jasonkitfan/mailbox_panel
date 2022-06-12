document.getElementById("facial").addEventListener("click", async () => {
    await eel.data_from_js(0);
    console.log("send 0 to python");
     document.body.style.backgroundImage = "url('/images/facial.gif')";
     document.getElementById("building-name").style.display="none";
     document.getElementById("device-panel").style.display="none";
     document.getElementById("layer-2").style.display="";
     document.getElementById("layer-3").style.display="";

})

document.getElementById("qr").addEventListener("click", async () => {
    await eel.data_from_js(1);
    console.log("send 1 to python");
    document.getElementById("layer-2").style.display="";
    document.body.style.backgroundImage = "url('/images/background.jpg')";
    document.getElementById("building-name").style.display="none";
    document.getElementById("device-panel").style.display="none";
    document.getElementById("layer-2").style.display="block";
    document.getElementById("layer-3").style.display="";

    py_video();
})

document.getElementById("pin").addEventListener("click", async () => {
    await eel.data_from_js(2);
    console.log("send 2 to python");
    document.body.style.backgroundImage = "url('/images/background.jpg')";
    document.getElementById("building-name").style.display="none";
    document.getElementById("device-panel").style.display="none";
    document.getElementById("layer-2").style.display="";
    document.getElementById("layer-3").style.display="block";
})

document.getElementById("cancel").addEventListener("click", async () => {
    await eel.data_from_js(3);
    console.log("send 3 to python");
    document.body.style.backgroundImage = "url('/images/background.jpg')";
    document.getElementById("building-name").style.display="";
    document.getElementById("device-panel").style.display="";
    document.getElementById("layer-2").style.display="";
    document.getElementById("layer-3").style.display="";

})


function py_video() {
    eel.video_feed()()
}


eel.expose(updateImageSrc);
function updateImageSrc(val) {
    let elem = document.getElementById('qr-cam');
    elem.src = "data:image/jpeg;base64," + val
}