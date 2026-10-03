
const API_BASE_URL="http://127.0.0.1:8000";


function obtenerHeadersAutenticacion(){
    //sirve para leer y recuperar un dato que guardaste previamente en la memoria del navegador., en este caso el token el cual nos dio al ingresar 
    const token=localStorage.item('token');
    return{
        //Soy el usuario con este pase digital (JWT). Revisa si tengo permiso para entrar."
        "Authorization": `Bearer ${token}`,

        //Te estoy enviando la información en estructura JSON (no en texto plano, ni como imagen, ni como formulario HTML)
        "Content-type": "application/json"
    };
}

//Dentro del parametro traer lo que yo necesito recibir para hacer el trabajo
async function apiCreacionPlan(datosPlan) {
    const respuesta = await fetch(`${API_BASE_URL}/planes/crear`, {
        method: "POST",
        // 1. Inyectamos los headers de autenticación (que ya incluyen Content-Type y Authorization)
        headers: obtenerHeadersAutenticacion(),
        //De Objeto en Memoria  A Cadena de Texto (para enviar).
        //En métodos que llevan un cuerpo de envío como POST, PUT o PATCH.
        body: JSON.stringify(datosPlan) 
    });

    //Toma esa cadena de texto recibida y la convierte en un objeto de memoria manipulable en JavaScript 

    const data = await respuesta.json();
    //Se usan los dos porque Necesitas tomar el objeto que preparaste en JavaScript y convertirlo a cadena de texto para enviárselo a FastAPI por la red.

    if (!respuesta.ok) {
       
        throw new Error("Hubo un error al crear el plan, intenta de nuevo.");
    }

    return data;
}

async function apiObtenerPlanesActivos(){
    const respuesta = await fetch (`${API_BASE_URL}/planes/obtener`,{
        method:"GET",
        headers:obtenerHeadersAutenticacion()

    });
    

    const data= await respuesta.json()

    if (!respuesta.ok){

        console.error("Error técnico desde FastAPI:", data.detail);

        //Creamos un nuevo error diferente para el del backend, para que el cliente no vea un erorr tan tecnico.
        throw new error("No se pudo obtener los planes activos, intenta de nuevo");
    }

    return data
}

async function apiAsignarMembresia(datosmembresia){
    const respuesta = await fetch (`${API_BASE_URL}/planes/asignar`,{
        method:"POST",
        headers:obtenerHeadersAutenticacion(),
        body:JSON.stringify(datosmembresia)

    });

    const data =await respuesta.json()

    if (!respuesta.ok){

        console.Error("Error técnico desde FastAPI:", data.detail);

        throw new Error("No se pudo asignar la membresia al usuario, intentelo de nuevo.");

    }

    return data


}

async function apiActualizarMembresia(usuario_id, datosactualizados) {
    
    const respuesta = await fetch(`${API_BASE_URL}/planes/actualizar-plan/${usuario_id}`, {
        method: "PUT",
        headers: obtenerHeadersAutenticacion(),
        body: JSON.stringify(datosactualizados)
    });

    // Desempaquetamos la respuesta en texto JSON de vuelta a un Objeto JS
    const data = await respuesta.json();

    if (!respuesta.ok) {
        console.error("Hubo un error en el backend FastAPI:", data.detail);

        // 🔴 3. Error va con E Mayúscula
        throw new Error("Hubo un error al actualizar la membresía, inténtalo de nuevo más tarde.");
    }

    return data;
}

async function apiVerMembresia(){
    const respuesta= await fetch (`${API_BASE_URL}/planes/mi-membresia`,{
        method:"GET",
        headers:obtenerHeadersAutenticacion(),

    });
    const data= await respuesta.json()

    if (!respuesta.ok){
        console.log("Hubo  un error en el backend FastAPI",data.detail)

        throw new error("Hubo un error al consultar estado de la membresia.")
    }

    return data

}







