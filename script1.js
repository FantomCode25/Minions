const startButton = document.getElementById('start-recording');
const transcriptElement = document.getElementById('transcript');

let mediaRecorder;
let audioChunks = [];

startButton.addEventListener('click', async () => {
    // Request microphone access
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.start();
    startButton.disabled = true; // Disable button while recording

    mediaRecorder.addEventListener('dataavailable', event => {
        audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener('stop', async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();

        // Here you can send the audioBlob to your server for STT processing
        // For example, using fetch to send the audio data
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav');

        const response = await fetch('/stt', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        transcriptElement.textContent = result.transcription; // Display the transcription
    });

    // Stop recording after a certain time (optional)
    setTimeout(() => {
        mediaRecorder.stop();
        startButton.disabled = false; // Re-enable button after recording
    }, 5000); // Stop recording after 5 seconds
});