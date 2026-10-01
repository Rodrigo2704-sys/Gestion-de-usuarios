// ====================================================================================
// 4. OPERACIONES CRUD DE USUARIOS (Conectado exactamente a tus Routers de Python)
//
// 💡 REGLA DE ORO DE LOS MÉTODOS HTTP Y EL BODY:
// -> SÍ LLEVAN BODY (POST y PUT): Se usa porque enviamos datos complejos al servidor
//    (un JSON completo con nombre, correo, etc.) que se empaquetan con JSON.stringify().
// -> NO LLEVAN BODY (GET y DELETE): El protocolo HTTP prohíbe que lleven cuerpo.
//    Los datos viajan de forma simple directamente escritos en la barra de direcciones (URL).
// ====================================================================================

/**
 * 2. REGISTRAR USUARIO (Ruta Pública - Corresponde a @router.post("/registrar"))
 * Envía un objeto JSON estructurado según tu esquema 'EntradaRegistro'
 */
const API_BASE_URL = "http://127.0.0.1:8000";

function obtenerHeadersAutenticacion() {
    const token = localStorage.getItem("token");
    return {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };
}

async function apiRegistrarUsuario(datosUsuario) {
    const respuesta = await fetch(`${API_BASE_URL}/usuarios/registrar`, {
        method: "POST", // POST indica que vamos a ENVIAR datos para crear un nuevo registro.
        headers: {
            "Content-Type": "application/json" // Avisa a FastAPI que le mandamos un JSON tradicional.
        },
        // NOTA: NO lleva token porque es una ruta pública para clientes nuevos.
        
        // SÍ LLEVA BODY: Traduce el objeto de JS a texto plano para que tu esquema lo reciba.
        body: JSON.stringify(datosUsuario) 
    });

    const data = await respuesta.json(); // Abre el paquete transformándolo en objeto JS.

    if (!respuesta.ok) {
        // Captura errores de negocio (ej: "El correo ya se encuentra registrado")
        throw new Error(data.detail || "No se pudo registrar el usuario");
    }
    return data; // Devuelve el objeto del usuario creado (SalidaUsuario)
}

/**
 * 3. OBTENER TODOS LOS USUARIOS (Ruta Protegida - Corresponde a @router.get("/"))
 */
async function apiListarUsuarios(skip = 0, limit = 100) {
    // Los parámetros viajan al final de la URL mapeando las variables de tu función de Python.
    const respuesta = await fetch(`${API_BASE_URL}/usuarios?skip=${skip}&limit=${limit}`, {
        method: "GET", // GET indica que solo estamos SOLICITANDO información de lectura.
        headers: obtenerHeadersAutenticacion() // Protegido: Envía la cabecera con tu Bearer JWT.
        // NO LLEVA BODY: Las consultas GET tienen prohibido llevar cuerpo.
    });

    const data = await respuesta.json(); // Abre la lista devuelta por el servidor.

    if (!respuesta.ok) {
        if (respuesta.status === 401) throw new Error("Sesión expirada o token inválido.");
        throw new Error(data.detail || "Error al obtener la lista de usuarios");
    }
    return data; // Devuelve la lista completa [SalidaUsuario, ...]
}

/**
 * 4. OBTENER USUARIO POR ID (Ruta Protegida - Corresponde a @router.get("/{usuario_id}"))
 */
async function apiObtenerUsuarioPorId(usuarioId) {
    // El ID viaja esculpido directamente dentro de la ruta URL de tu endpoint.
    const respuesta = await fetch(`${API_BASE_URL}/usuarios/${usuarioId}`, {
        method: "GET", // Sigue siendo una petición de lectura.
        headers: obtenerHeadersAutenticacion() // Valida la identidad del administrador.
        // NO LLEVA BODY: El ID ya fue enviado arriba en la dirección.
    });

    const data = await respuesta.json(); 

    if (!respuesta.ok) {
        throw new Error(data.detail || "Usuario no encontrado");
    }
    return data; // Devuelve los detalles exclusivos de ese ID específico.
}

/**
 * 5. ACTUALIZAR USUARIO (Ruta Protegida - Corresponde a @router.put("/{usuario_id}"))
 * Envía los campos que deseas modificar según tu esquema 'ActualizarUsuario'
 */
async function apiModificarUsuario(usuarioId, datosActualizacion) {
    // El ID va en la dirección para saber a quién editar, y los datos nuevos viajan en el body.
    const respuesta = await fetch(`${API_BASE_URL}/usuarios/${usuarioId}`, {
        method: "PUT", // PUT le indica a SQLAlchemy que modificaremos un registro existente.
        headers: obtenerHeadersAutenticacion(), 
        
        // SÍ LLEVA BODY: Empaqueta los cambios parciales que filtrará tu .model_dump(exclude_unset=True).
        body: JSON.stringify(datosActualizacion) 
    });

    const data = await respuesta.json(); 

    if (!respuesta.ok) {
        throw new Error(data.detail || "Error al actualizar el usuario");
    }
    return data; // Devuelve el objeto ya modificado en la base de datos.
}

/**
 * 6. ELIMINAR USUARIO (Ruta Protegida - Corresponde a @router.delete("/{usuario_id}"))
 */
async function apiBorrarUsuario(usuarioId) {
    const respuesta = await fetch(`${API_BASE_URL}/usuarios/${usuarioId}`, {
        method: "DELETE", // Da la orden estricta a SQLAlchemy de borrar físicamente la fila.
        headers: obtenerHeadersAutenticacion() // Requiere token activo.
        // NO LLEVA BODY: Solo requiere el ID mapeado en la URL.
    });

    const data = await respuesta.json(); 

    if (!respuesta.ok) {
        throw new Error(data.detail || "No se pudo eliminar el usuario");
    }
    return data; // Devuelve tu objeto de confirmación: {"Exito": true, "Mensaje": "Usuario eliminado..."}
}

/**
 * 7. BUSCAR USUARIO POR CORREO (Ruta Protegida - Corresponde al endpoint opcional)
 */
async function apiObtenerUsuarioPorCorreo(correoElectronico) {
    const urlConQuery = `${API_BASE_URL}/usuarios/buscar/correo?email=${encodeURIComponent(correoElectronico)}`;
    
    const respuesta = await fetch(urlConQuery, {
        method: "GET",
        headers: obtenerHeadersAutenticacion()
    });

    const data = await respuesta.json();

    if (!respuesta.ok) {
        throw new Error(data.detail || "No se encontró el correo");
    }
    return data; 
}
