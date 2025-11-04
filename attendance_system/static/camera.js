// static/camera.js

const videoElement = document.getElementById('videoElement');
const cameraSelection = document.getElementById('cameraSelection');
const canvasElement = document.getElementById('canvasElement');
const context = canvasElement.getContext('2d');
const photoPreview = document.getElementById('photoPreview');
const captureButton = document.getElementById('captureButton');
const submitButton = document.getElementById('submitButton');
const retryButton = document.getElementById('retryButton');
const statusMessage = document.getElementById('statusMessage');
const photoDataInput = document.getElementById('photoData');
let currentStream;

// Function to stop the current video stream tracks
function stopMediaTracks(stream) {
    if (stream) {
        stream.getTracks().forEach(track => {
            track.stop();
        });
    }
}

// Function to get camera access with specific constraints (deviceId)
async function getCameraStream(deviceId) {
    stopMediaTracks(currentStream); // Stop previous stream

    const constraints = {
        video: {
            deviceId: deviceId ? { exact: deviceId } : undefined,
            width: { ideal: 640 },
            height: { ideal: 480 }
        }
    };

    try {
        // This call prompts the user for permission the first time
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        currentStream = stream;
        videoElement.srcObject = stream;

        // Once permission is granted, we can populate the dropdown labels reliably
        if (cameraSelection.options.length === 0 || cameraSelection.options[0].text.includes('Camera')) {
            populateCameraList();
        }
    } catch (err) {
        console.error("Error accessing the camera: ", err);
        statusMessage.textContent = "Error: Could not access camera. Please allow permissions.";
        statusMessage.className = 'error';
    }
}

// Function to list all available video input devices and populate the dropdown
async function populateCameraList() {
    // We can only get proper labels *after* getUserMedia has run successfully once
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoInputs = devices.filter(device => device.kind === 'videoinput');

    cameraSelection.innerHTML = ''; // Clear previous list
    videoInputs.forEach(device => {
        const option = document.createElement('option');
        option.value = device.deviceId;
        // The device.label will be available now
        option.text = device.label || `Camera ${cameraSelection.options.length + 1}`;
        cameraSelection.appendChild(option);
    });
}

// Event handler for the "Apply" button
function applyCameraSettings() {
    const selectedDeviceId = cameraSelection.value;
    if (selectedDeviceId) {
        getCameraStream(selectedDeviceId);
    }
}

// --- Capture and Submission Logic ---

captureButton.addEventListener('click', () => {
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
    const imageDataUrl = canvasElement.toDataURL('image/png');

    photoPreview.src = imageDataUrl;
    photoDataInput.value = imageDataUrl;

    photoPreview.classList.remove('hidden');
    videoElement.classList.add('hidden');
    captureButton.classList.add('hidden');
    submitButton.classList.remove('hidden');
    retryButton.classList.remove('hidden');

    statusMessage.textContent = "Photo captured. Click submit to log attendance.";
    statusMessage.className = '';
});

submitButton.addEventListener('click', () => {
    const photoDataValue = photoDataInput.value;
    statusMessage.textContent = "Sending data to server...";
    statusMessage.className = 'info';

    fetch('/log_attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ imageData: photoDataValue }),
    })
        .then(response => response.json())
        .then(data => {
            statusMessage.textContent = data.message;
            if (data.status === "success") {
                statusMessage.className = 'success';
            } else {
                statusMessage.className = 'error';
            }
            setTimeout(resetCapture, 5000);
        })
        .catch((error) => {
            console.error('Error:', error);
            statusMessage.textContent = "Network error occurred.";
            statusMessage.className = 'error';
        });
});

function resetCapture() {
    videoElement.classList.remove('hidden');
    photoPreview.classList.add('hidden');
    captureButton.classList.remove('hidden');
    submitButton.classList.add('hidden');
    retryButton.classList.add('hidden');
    photoDataInput.value = '';
    statusMessage.textContent = "Ready to capture attendance.";
    statusMessage.className = '';
}

// Initialize the camera stream immediately on page load to prompt permission
document.addEventListener('DOMContentLoaded', (event) => {
    getCameraStream();
});
