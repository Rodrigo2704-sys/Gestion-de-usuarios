// Guarda este código dentro de tu archivo: login.js
document.getElementById("iniciarsesion").addEventListener("submit", async function(e) {
    e.preventDefault(); // Evita que la página se recargue sola

    const correo = document.getElementById("correo").value;
    const password = document.getElementById("password").value;
    
    // Referencia al botón para deshabilitarlo durante la carga
    const botonSubmit = e.target.querySelector("button[type='submit']");
    if (botonSubmit) botonSubmit.disabled = true;

    // Codificación de datos obligatoria para OAuth2PasswordRequestForm
    const formData = new URLSearchParams();

    // append porque para que en la pagina se vea correo y contraseña,  porque así lo exige el estándar de FastAPI (OAuth2PasswordRequestForm), pero adentro le guardas el valor de la variable correo que escribió el usuario.
    formData.append("username", correo);
    formData.append("password", password);

    try {
        // CORREGIDO: Aquí pusimos la URL completa de tu backend con su puerto local
        const respuesta = await fetch("http://127.0.0.1:8000/usuarios/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        // Capturamos el JSON de respuesta tanto si es exitoso como si da error
        const data = await respuesta.json();

        if (!respuesta.ok) {
            // Si el backend lanza el HTTPException(401), el mensaje viene en data.detail
            throw new Error(data.detail || "Correo o contraseña incorrectos");
        }
        
        // --- GUARDADO SEGURO DE SESIÓN ---
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("nombre_usuario", data.nombre);
        
        // Redirección inmediata a la vista de administración
        window.location.href = "usuarios.html";

    } catch (error) {
        alert("Error de autenticación: " + error.message);
        console.error("Detalle del error:", error);
    } finally {
        // Volvemos a habilitar el botón si la petición terminó (con o sin error)
        if (botonSubmit) botonSubmit.disabled = false;
    }
});
