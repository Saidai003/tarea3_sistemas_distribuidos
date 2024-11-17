-- Crear el keyspace "traffic" con estrategia de replicación simple
CREATE KEYSPACE IF NOT EXISTS traffic 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

-- Seleccionar el keyspace
USE traffic;

-- Crear la tabla para almacenar eventos históricos
CREATE TABLE IF NOT EXISTS historical_events (
    id UUID PRIMARY KEY,
    type TEXT,
    location TEXT,
    severity TEXT,
    timestamp TIMESTAMP
);
