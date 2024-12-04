document.addEventListener('DOMContentLoaded', () => {
    const githubButton = document.getElementById('github');
    const linkedinButton = document.getElementById('linkedin');
    const submitButton = document.getElementById('submit');
    const downloadButton = document.getElementById('download');
    const inputField = document.getElementById('Q');
    const respuestaContainer = document.getElementById('respuesta');
    const versionSelector = document.getElementById('versionSelector');

    // Evento para enviar pregunta
    submitButton.addEventListener('click', () => {
        const pregunta = inputField.value.trim();
        if (pregunta) {
            respuestaContainer.textContent = `Procesando tu pregunta: "${pregunta}"...`;
            // Aquí puedes incluir la lógica para enviar la pregunta a la API de JarvisIA
        } else {
            respuestaContainer.textContent = 'Por favor, escribe una pregunta.';
        }
    });

    // Botón de GitHub
    githubButton.addEventListener('click', () => {
        window.open('https://github.com/Jordan-Iralde/ProBestoJarvisAI', '_blank');
    });

    // Botón de LinkedIn
    linkedinButton.addEventListener('click', () => {
        window.open('https://www.linkedin.com/in/jordan-iralde/', '_blank');
    });

    // Botón de Descarga
    downloadButton.addEventListener('click', () => {
        const downloadUrl = 'https://github.com/Jordan-Iralde/ProBestoJarvisAI/releases/download/v3/JarvisIA_v3.exe';
        window.open(downloadUrl, '_blank');
    });
});
