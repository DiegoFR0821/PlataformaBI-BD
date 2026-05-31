-- =======================================================
-- PROYECTO: Plataforma BI & Big Data - Seguridad Lima Norte
-- ARQUITECTURA: Modelo Copo de Nieve (Snowflake Schema)
-- =======================================================

USE master;
GO
DROP DATABASE IF EXISTS NightWatch_DB;
GO
CREATE DATABASE NightWatch_DB;
GO
USE NightWatch_DB;
GO

-- 1. CONTROL DE ACCESO (PLATAFORMA WEB)
CREATE TABLE Usuarios (
    ID_Usuario INT IDENTITY(1,1) PRIMARY KEY,
    Username   VARCHAR(100) NOT NULL,
    Password   VARCHAR(100) NOT NULL
);
INSERT INTO Usuarios (Username, Password) VALUES ('admin@gmail.com', '123456');
GO

-- 2. CAPA STAGING (Soporte transaccional ETL)
CREATE TABLE Staging_Reportes_Policiales (
    ID_Carga             INT IDENTITY(1,1) PRIMARY KEY,
    Fecha_Reporte        DATE,
    Hora_Reporte         TIME,
    Distrito             VARCHAR(100),
    Tipo_Delito          VARCHAR(100),
    Latitud              FLOAT,
    Longitud             FLOAT,
    Tiempo_Respuesta_Min FLOAT,
    Uso_Arma             VARCHAR(10),
    Captura              VARCHAR(10),
    Rango_Horario        VARCHAR(50),
    Estado_Limpieza      VARCHAR(50)
);
GO

-- 3. DATA WAREHOUSE: SUB-DIMENSIONES (Copo de Nieve)
CREATE TABLE Dim_Distrito (
    ID_Distrito     INT IDENTITY(1,1) PRIMARY KEY,
    Nombre_Distrito VARCHAR(100) NOT NULL,
    Zona_Lima       VARCHAR(50) DEFAULT 'Lima Norte'
);

CREATE TABLE Dim_Categoria_Delito (
    ID_Categoria     INT IDENTITY(1,1) PRIMARY KEY,
    Nombre_Categoria VARCHAR(100) NOT NULL,
    Severidad_Base   VARCHAR(50)
);
GO

-- 4. DATA WAREHOUSE: DIMENSIONES NODALES
CREATE TABLE Dim_Ubicacion (
    ID_Ubicacion INT IDENTITY(1,1) PRIMARY KEY,
    Latitud      FLOAT NOT NULL,
    Longitud     FLOAT NOT NULL,
    ID_Distrito  INT FOREIGN KEY REFERENCES Dim_Distrito(ID_Distrito)
);

CREATE TABLE Dim_Delito (
    ID_Delito    INT IDENTITY(1,1) PRIMARY KEY,
    Nombre_Delito VARCHAR(100) NOT NULL,
    ID_Categoria INT FOREIGN KEY REFERENCES Dim_Categoria_Delito(ID_Categoria)
);

CREATE TABLE Dim_Tiempo (
    ID_Tiempo     INT IDENTITY(1,1) PRIMARY KEY,
    Fecha         DATE NOT NULL,
    Anio          INT,
    Mes           INT,
    Dia           INT,
    Hora_Completa TIME,
    Rango_Horario VARCHAR(50)
);
GO

-- 5. DATA WAREHOUSE: TABLA DE HECHOS CENTRAL
CREATE TABLE Fact_Incidentes (
    ID_Hecho             INT IDENTITY(1,1) PRIMARY KEY,
    ID_Tiempo            INT FOREIGN KEY REFERENCES Dim_Tiempo(ID_Tiempo),
    ID_Ubicacion         INT FOREIGN KEY REFERENCES Dim_Ubicacion(ID_Ubicacion),
    ID_Delito            INT FOREIGN KEY REFERENCES Dim_Delito(ID_Delito),
    Tiempo_Respuesta_Min FLOAT NOT NULL,
    Uso_Arma             VARCHAR(10),
    Captura              VARCHAR(10),
    Cantidad             INT DEFAULT 1
);
GO