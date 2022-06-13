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

document.getElementById("cancel").addEventListener("click", returnMainPage)

async function returnMainPage(){
    await eel.data_from_js(3);
    console.log("send 3 to python");
    document.body.style.backgroundImage = "url('/images/background.jpg')";
    document.getElementById("building-name").style.display="";
    document.getElementById("device-panel").style.display="";
    document.getElementById("layer-2").style.display="";
    document.getElementById("layer-3").style.display="";
}


function py_video() {
    eel.video_feed()()
}


eel.expose(updateImageSrc);
function updateImageSrc(val) {
    let elem = document.getElementById('qr-cam');
    elem.src = "data:image/jpeg;base64," + val
}

eel.expose(showValid)
function showValid(flat, color){
    document.getElementById("flat-info").innerHTML = `Mailbox ${flat} is opening`;
    document.getElementById("flat-info").style.color = color;
    let x = document.getElementById("layer-4")
    x.style.backgroundImage = "url(images/success.gif)";
    x.style.display = "block";
    reset();
    setTimeout(function(){x.style.display = ""}, 6000);
    returnMainPage();
}

eel.expose(showInvalid)
function showInvalid(color){
    document.getElementById("flat-info").innerHTML = "Invalid input";
    document.getElementById("flat-info").style.color = color;
    let x = document.getElementById("layer-4")
    x.style.backgroundImage = "url(images/failure.gif)";
    x.style.display = "block";
    reset();
    setTimeout(function(){x.style.display = ""}, 6000);
    returnMainPage();
}

let input = "";

function inputCheck(val){
    for(let i=1; i <= val.length; i++){
        document.getElementById(`input-${i}`).innerHTML = val[i - 1];
    }
    if(val.length >= 6){
        eel.check_input(val);
    }
}

document.getElementById("key-1").addEventListener("click", async () => {
    input += "1";
    inputCheck(input);
});

document.getElementById("key-2").addEventListener("click", async () => {
    input += "2";
    inputCheck(input);
});

document.getElementById("key-3").addEventListener("click", async () => {
    input += "3";
    inputCheck(input);
});

document.getElementById("key-4").addEventListener("click", async () => {
    input += "4";
    inputCheck(input);
});

document.getElementById("key-5").addEventListener("click", async () => {
    input += "5";
    inputCheck(input);
});

document.getElementById("key-6").addEventListener("click", async () => {
    input += "6";
    inputCheck(input);
});

document.getElementById("key-7").addEventListener("click", async () => {
    input += "7";
    inputCheck(input);
});

document.getElementById("key-8").addEventListener("click", async () => {
    input += "8";
    inputCheck(input);
});


document.getElementById("key-9").addEventListener("click", async () => {
    input += "9";
    inputCheck(input);
});


document.getElementById("key-0").addEventListener("click", async () => {
    input += "0";
    inputCheck(input);
});

document.getElementById("key-reset").addEventListener("click", async () => {
    reset();
});

document.getElementById("key-del").addEventListener("click", async () => {
    if(input.length != 0){
        input = input.slice(0, input.length - 1);
        document.getElementById(`input-${input.length + 1}`).innerHTML = " - ";
    }
})

function reset(){
    input = "";
    for(let i=1; i <7; i++){
        document.getElementById(`input-${i}`).innerHTML = " - ";
    }
}