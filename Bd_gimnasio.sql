create database if not exists FastAPI;
use fastapi;
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);


-- Tabla de planes del gimnasio
CREATE TABLE IF NOT EXISTS planes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(100) NOT NULL,       -- Nombre del plan (ej. 'Mensual', 'Trimestral')
    precio DECIMAL(10,2) NOT NULL,    -- Precio (ajustado a 2 decimales para centavos)
    duracion INT NOT NULL,            -- Cantidad de días de vigencia (ej. 30, 90, 365)
    estado VARCHAR(50) DEFAULT 'activo' -- Estado ('activo', 'inactivo')
);

-- Tabla de membresías vendidas/asignadas a los usuarios
CREATE TABLE IF NOT EXISTS membresias_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    plan_id INT NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    estado VARCHAR(50) DEFAULT 'activa', -- Estado ('activa', 'vencida', 'cancelada')
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES planes(id) ON DELETE CASCADE
);

INSERT INTO planes (tipo, precio, duracion, estado) 
VALUES 
('Plan Mensual', 80000.00, 30, 'activo'),
('Plan Trimestral', 220000.00, 90, 'activo'),
('Plan Anual', 800000.00, 365, 'activo');

