# ============================================
# AcademiX — database.py
# Conexión a SQLite y creación automática
# de todas las tablas al iniciar.
# ============================================

import sqlite3
from backend.config import DATABASE


def get_connection():
    """Retorna una conexión a la base de datos con row_factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row   # permite acceder a columnas por nombre
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea todas las tablas si no existen. Se llama al iniciar la app."""
    conn = get_connection()
    cursor = conn.cursor()

    # — Tabla: actividades —
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            mes              TEXT,
            periodo          TEXT,
            fecha_inicio     TEXT,
            fecha_fin        TEXT,
            tipologia        TEXT,
            modalidad        TEXT,
            programa         TEXT,
            nombre           TEXT NOT NULL,
            descripcion      TEXT,
            objetivo         TEXT,
            num_participantes INTEGER DEFAULT 0,
            horas_dedicadas  INTEGER DEFAULT 0,
            recursos         TEXT,
            resultados       TEXT,
            observaciones    TEXT,
            creado_en        TEXT DEFAULT (datetime('now')),
            actualizado_en   TEXT DEFAULT (datetime('now'))
        )
    """)

    # — Tabla: usuarios —
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT NOT NULL,
            correo    TEXT NOT NULL UNIQUE,
            password  TEXT NOT NULL,
            rol       TEXT DEFAULT 'docente',   -- 'admin' | 'docente'
            facultad  TEXT,
            creado_en TEXT DEFAULT (datetime('now'))
        )
    """)

    # — Tabla: historial —
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo        TEXT NOT NULL,   -- 'creacion' | 'edicion' | 'eliminacion'
            titulo      TEXT NOT NULL,
            descripcion TEXT,
            usuario     TEXT DEFAULT 'Sistema',
            fecha       TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    print("[AcademiX] Base de datos lista ✓")