// =======================================================================
// SECCIÓN 1: ESTO SE EJECUTA ADENTRO DE USUARIOS.HTML APENAS CARGA LA PÁGINA
// 📌 ¿DÓNDE ESTÁ EL LOGIN Y EL REGISTRO? (Tus 2 APIs públicas)
// -> API 1 (POST /usuarios/login): Se ejecutó antes en 'login.js'. Dejó el Token en el localStorage.
// -> API 2 (POST /usuarios/registrar): Se ejecuta en tu vista de alta/registro (pública).
// =======================================================================
document.addEventListener("DOMContentLoaded", async function() {
    const token = localStorage.getItem("token");
    const nombre = localStorage.getItem("nombre_usuario");

    // Control de intrusos: Si no hay token, lo echamos al login
    if (!token) {
        alert("Acceso denegado. Por favor, inicia sesión.");
        window.location.href = "login.html"; 
        return;
    }

    // Saludo: Pintamos el nombre del usuario que inició sesión
    const contenedorNombre = document.getElementById("nombre-bienvenida");
    if (contenedorNombre && nombre) {
        contenedorNombre.textContent = nombre;
    }

    // Apenas carga la pantalla, llamamos de inmediato a la Sección 2 (API 3)
    await mostrarTablaDeUsuarios();
});

// =======================================================================
// SECCIÓN 2: ACCIÓN -> LISTAR TODOS LOS USUARIOS
// 🏛️ EJECUTA LA API 3: GET /usuarios/
// -> Llama a tu router de Python '@router.get("/")'. Trae el arreglo completo
//    con todos los clientes registrados en la base de datos del gimnasio.
// =======================================================================
async function mostrarTablaDeUsuarios() {
    try {
        const listaUsuarios = await apiListarUsuarios(); // Consume la API 3
        const tabla = document.getElementById("cuerpo-tabla-usuarios");
        
        if (!tabla) return;
        tabla.innerHTML = ""; 

        listaUsuarios.forEach(u => {
            tabla.innerHTML += `
                <tr>
                    <td>${u.id}</td>
                    <td>${u.nombre}</td>
                    <td>${u.correo}</td>
                    <td>
                        <!-- Al dar clic en Editar, viaja el ID a la Sección 3 (API 4) -->
                        <button onclick="prepararEdicionYBuscarPorId(${u.id})">Editar</button>
                        <button onclick="eliminarUsuarioDelGym(${u.id})">Eliminar</button>
                    </td>
                </tr>
            `;
        });
    } catch (error) {
        alert("Error al cargar la lista: " + error.message);
    }
}

// =======================================================================
// SECCIÓN 3: ACCIÓN -> BUSCAR USUARIO POR ID
// 🏛️ EJECUTA LA API 4: GET /usuarios/{usuario_id}
// -> Se activa al pulsar el botón "Editar" en la tabla. Llama a tu router 
//    '@router.get("/{usuario_id}")' para traer la información exclusiva de ese ID 
//    y rellenar los campos de texto antes de modificarlos.
// =======================================================================
async function prepararEdicionYBuscarPorId(usuarioId) {
    try {
        const usuarioEncontrado = await apiObtenerUsuarioPorId(usuarioId); // Consume la API 4
        
        // Buscamos los inputs de tu formulario de edición en el HTML
        const inputId = document.getElementById("edit-id");
        const inputNombre = document.getElementById("edit-nombre");
        const inputCorreo = document.getElementById("edit-correo");

        // Rellenamos el formulario automáticamente con los datos reales que nos devolvió el ID
        if (inputNombre && inputCorreo) {
            if (inputId) inputId.value = usuarioEncontrado.id; // Guardamos el ID en un input oculto
            inputNombre.value = usuarioEncontrado.nombre;      // Escribe el nombre en el cuadro de texto
            inputCorreo.value = usuarioEncontrado.correo;      // Escribe el correo en el cuadro de texto
            
            alert(`Campos rellenos con los datos del usuario ID: ${usuarioEncontrado.id}`);
        }
    } catch (error) {
        alert("No se pudo obtener el usuario por ID: " + error.message);
    }
}

// =======================================================================
// SECCIÓN 4: ACCIÓN -> GUARDAR LOS CAMBIOS DE LA EDICIÓN (MÉTODO PUT)
// 🏛️ EJECUTA LA API 5: PUT /usuarios/{usuario_id}
// -> Se activa al presionar "Guardar Cambios". Llama a tu router '@router.put("/{usuario_id}")'
//    enviando el JSON parcial para actualizar el registro en tu base de datos.
// =======================================================================
async function ejecutarModificacionUsuario() {
    // Jalamos los valores que están escritos actualmente en los cuadros de texto
    const usuarioId = document.getElementById("edit-id").value;
    const datosActualizados = {
        nombre: document.getElementById("edit-nombre").value,
        correo: document.getElementById("edit-correo").value
    };

    if (confirm("¿Confirmar cambios de edición?")) {
        try {
            await apiModificarUsuario(usuarioId, datosActualizados); // Consume la API 5
            alert("¡Usuario actualizado con éxito!");
            await mostrarTablaDeUsuarios(); // Refrescamos la tabla para ver el cambio reflejado (API 3)
        } catch (error) {
            alert("Error al actualizar: " + error.message);
        }
    }
}

// =======================================================================
// SECCIÓN 5: ACCIÓN -> BUSCAR USUARIO POR CORREO
// 🏛️ EJECUTA LA API 6: GET /usuarios/buscar/correo (Endpoint de búsqueda)
// -> Se activa cuando el administrador escribe un email y presiona "Buscar".
//    Llama al router de búsqueda para filtrar la tabla y mostrar un solo cliente.
// =======================================================================
async function buscarClienteEspecificoPorCorreo() {
    // Capturamos lo que el administrador escribió en la barra de búsqueda
    const correoBuscado = document.getElementById("input-busqueda-correo").value;
    
    if (!correoBuscado) {
        alert("Por favor, ingresa un correo electrónico en la barra de búsqueda.");
        return;
    }

    try {
        const usuarioEncontrado = await apiObtenerUsuarioPorCorreo(correoBuscado); // Consume la API 6
        
        // Limpiamos la tabla del gimnasio y pintamos UNICAMENTE al usuario que encontramos
        const tabla = document.getElementById("cuerpo-tabla-usuarios");
        if (tabla) {
            tabla.innerHTML = `
                <tr>
                    <td>${usuarioEncontrado.id}</td>
                    <td>${usuarioEncontrado.nombre}</td>
                    <td>${usuarioEncontrado.correo}</td>
                    <td>
                        <button onclick="prepararEdicionYBuscarPorId(${usuarioEncontrado.id})">Editar</button>
                        <button onclick="eliminarUsuarioDelGym(${usuarioEncontrado.id})">Eliminar</button>
                    </td>
                </tr>
            `;
        }
    } catch (error) {
        alert("Búsqueda fallida: " + error.message);
    }
}

// =======================================================================
// SECCIÓN 6: ACCIÓN -> ELIMINAR USUARIO
// 🏛️ EJECUTA LA API 7: DELETE /usuarios/{usuario_id}
// -> Se activa al presionar el botón "Eliminar". Llama a tu router '@router.delete("/{usuario_id}")'
//    para borrar físicamente la fila del cliente usando SQLAlchemy.
// =======================================================================
async function eliminarUsuarioDelGym(usuarioId) {
    if (confirm(`¿Estás seguro de que deseas eliminar al usuario con ID: ${usuarioId}?`)) {
        try {
            const respuesta = await apiBorrarUsuario(usuarioId); // Consume la API 7
            alert(respuesta.Mensaje); 
            await mostrarTablaDeUsuarios(); // Recargamos la lista para borrar la fila visualmente (API 3)
        } catch (error) {
            alert("No se pudo eliminar: " + error.message);
        }
    }
}
