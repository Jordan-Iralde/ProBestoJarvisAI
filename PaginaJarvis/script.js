document.querySelector("button").addEventListener("click", function() {
    const pregunta = document.getElementById("Q").value;
    if (pregunta) {
        document.querySelector(".Container p").innerText = `Respuesta a tu pregunta: ${pregunta}`;
    } else {
        document.querySelector(".Container p").innerText = "Por favor, escribe una pregunta.";
    }
});