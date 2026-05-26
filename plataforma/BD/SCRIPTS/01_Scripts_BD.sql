-- 1. Crear la base de datos
CREATE DATABASE NightWatch_DB;
GO

-- Usar la base de datos recién creada
USE NightWatch_DB;
GO


-- 2. Crear tabla de Staging (Datos Crudos)
-- Creamos la tabla con TODAS las columnas del nuevo CSV
CREATE TABLE Staging_Reportes_Policiales (
    ID_Carga INT IDENTITY(1,1) PRIMARY KEY,
    Fecha_Reporte DATE,
    Hora_Reporte TIME,
    Distrito VARCHAR(100),
    Tipo_Delito VARCHAR(100),
    Latitud FLOAT,
    Longitud FLOAT,
    Tiempo_Respuesta_Min FLOAT,
    Uso_Arma VARCHAR(10),
    Captura VARCHAR(10),
    Rango_Horario VARCHAR(50),
    Estado_Limpieza VARCHAR(50)
);
GO
-- 3A. Crear Dimensiones (Tablas de Catálogo)

CREATE TABLE Dim_Ubicacion (
    ID_Ubicacion INT IDENTITY(1,1) PRIMARY KEY,
    Distrito VARCHAR(100),
    Zona_Sector VARCHAR(50)
);

CREATE TABLE Dim_Tiempo (
    ID_Tiempo INT IDENTITY(1,1) PRIMARY KEY,
    Fecha DATE,
    Anio INT,
    Mes INT,
    Dia INT,
    Rango_Horario VARCHAR(20) -- Ej. 'Mañana', 'Tarde', 'Noche'
);

CREATE TABLE Dim_Tipo_Delito (
    ID_Tipo_Delito INT IDENTITY(1,1) PRIMARY KEY,
    Categoria VARCHAR(100),
    Gravedad VARCHAR(20)      -- Ej. 'Alta', 'Media', 'Baja'
);

-- 3B. Crear Tabla de Hechos (El corazón de tu análisis)

CREATE TABLE Fact_Incidentes_Seguridad (
    ID_Incidente INT IDENTITY(1,1) PRIMARY KEY,
    ID_Tiempo INT FOREIGN KEY REFERENCES Dim_Tiempo(ID_Tiempo),
    ID_Ubicacion INT FOREIGN KEY REFERENCES Dim_Ubicacion(ID_Ubicacion),
    ID_Tipo_Delito INT FOREIGN KEY REFERENCES Dim_Tipo_Delito(ID_Tipo_Delito),
    
    -- Métricas (KPIs)
    Cantidad_Delitos INT DEFAULT 1,
    Tiempo_Respuesta_Minutos FLOAT
);
GO