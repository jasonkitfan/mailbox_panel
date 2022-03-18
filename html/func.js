//async function getDataFromPython(){
//   document.getElementById('myele').innerText = await eel.get_data()();
//}
//
//document.getElementById('qr').addEventListener('click', () => {
//   getDataFromPython();
//})

document.getElementById('facial').addEventListener('click', async () => {
    await eel.data_from_js(0);
    console.log("send 0 to python");
     document.body.style.backgroundImage = "url('/images/facial.gif')";
     document.getElementById("building-name").style.display='none';
     document.getElementById("device-panel").style.display='none';
     document.getElementById("layer-2").style.display='';
})

document.getElementById('qr').addEventListener('click', async () => {
    await eel.data_from_js(1);
    console.log("send 1 to python");
    document.getElementById("layer-2").style.display="";
    document.body.style.backgroundImage = "url('/images/background.jpg')";
    document.getElementById("building-name").style.display='none';
    document.getElementById("device-panel").style.display='none';
    document.getElementById("layer-2").style.display='block';
})

document.getElementById('pin').addEventListener('click', async () => {
    await eel.data_from_js(2);
    console.log("send 2 to python");
    document.getElementById("building-name").style.display='none';
    document.getElementById("device-panel").style.display='none';
    document.getElementById("layer-2").style.display='';
})

document.getElementById('cancel').addEventListener('click', async () => {
    await eel.data_from_js(3);
    console.log("send 3 to python");
    document.body.style.backgroundImage = "url('/images/background.jpg')";
    document.getElementById("building-name").style.display='';
    document.getElementById("device-panel").style.display='';
    document.getElementById("layer-2").style.display='';

})
