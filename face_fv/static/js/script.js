let video;
let canvas;
let nameInput;
let stream; // Variable to store the video stream

function init(){
    video = document.getElementById("video")
    canvas = document.getElementById("canvas")
    nameInput = document.getElementById("name")

    navigator.mediaDevices.getUserMedia({video:true})
        .then(str=>{
            stream = str; // Store the video stream
            video.srcObject = stream;
        })
        .catch(error=>{
            console.log("error accessing webcam", error);
            alert("Cannot access webcam.");
        });
}

function stopCamera() {
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop()); // Stop all tracks in the stream
        video.srcObject = null; // Release the video stream
    }
}

function capture(){
    const context = canvas.getContext("2d")
    context.drawImage(video,0,0,canvas.width,canvas.height)
    canvas.style.display = "block"
    video.style.display = "none"
}

function register(){
    const name = nameInput.value
    const photo = dataURItoBlob(canvas.toDataURL())

    if(!name || !photo){
        alert("Name and photo are required, please.")
        return
    }

    const formData = new FormData()
    formData.append("name",name)
    formData.append('photo', photo, `${name}.jpg`);

    fetch("/register",{
        method:"POST",
        body:formData
    })
    .then(response=>response.json())
    .then(data=>{
        if(data.success){
            alert("Data successfully registered.")
            stopCamera(); // Stop the camera after successful registration
            window.location.href="/login"
        }
        else{
            alert("Sorry, registration failed.")
        }
    })
    .catch(error=>{
        console.log("Error", error);
    })
}

function dataURItoBlob(dataURI){
    const byteString = atob(dataURI.split(",")[1])
    const mimeString = dataURI.split(",")[0].split(":")[1].split(";")[0]

    const ab = new ArrayBuffer(byteString.length)
    const ia = new Uint8Array(ab)
    for(let i=0; i<byteString.length;i++)
    {
        ia[i]=byteString.charCodeAt(i)
    }
    return new Blob([ab],{type:mimeString})
}

init();
