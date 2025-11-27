-- ============================================================================
-- SCRIPT SQL PARA CREAR TABLAS EN SUPABASE
-- ============================================================================
-- 
-- INSTRUCCIONES:
-- 1. Ve a tu proyecto en Supabase: https://supabase.com/dashboard
-- 2. Click en "SQL Editor" en el menú lateral
-- 3. Copia y pega este script completo
-- 4. Click en "Run" para ejecutar
-- 
-- Este script creará 3 tablas:
-- - logs: Registros de todas las consultas
-- - users: Información de usuarios (opcional, para futuro)
-- - sessions: Tracking de sesiones (opcional, para futuro)
-- ============================================================================

-- ============================================================================
-- TABLA: logs
-- ============================================================================
-- Almacena TODOS los logs de consultas de forma permanente
-- A diferencia de Redis (temporal), estos datos nunca expiran

CREATE TABLE IF NOT EXISTS logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    response_time_ms FLOAT DEFAULT 0,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para mejorar performance de queries
CREATE INDEX IF NOT EXISTS idx_logs_user_id ON logs(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_session_id ON logs(session_id);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp DESC);

-- Comentarios para documentación
COMMENT ON TABLE logs IS 'Logs permanentes de todas las consultas al chatbot';
COMMENT ON COLUMN logs.user_id IS 'ID del usuario que hizo la consulta';
COMMENT ON COLUMN logs.session_id IS 'ID único de la sesión conversacional';
COMMENT ON COLUMN logs.user_message IS 'Mensaje enviado por el usuario';
COMMENT ON COLUMN logs.bot_response IS 'Respuesta generada por el bot';
COMMENT ON COLUMN logs.response_time_ms IS 'Tiempo de respuesta en milisegundos';
COMMENT ON COLUMN logs.timestamp IS 'Momento exacto de la consulta';


-- ============================================================================
-- TABLA: users (OPCIONAL - Para futuro)
-- ============================================================================
-- Almacena información de usuarios
-- Útil para autenticación, perfiles, etc.

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'student', -- 'student', 'teacher', 'admin'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Comentarios
COMMENT ON TABLE users IS 'Información de usuarios de la plataforma';
COMMENT ON COLUMN users.role IS 'Rol del usuario: student, teacher, admin';


-- ============================================================================
-- TABLA: sessions (OPCIONAL - Para futuro)
-- ============================================================================
-- Tracking de sesiones conversacionales
-- Útil para analytics y debugging

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    total_messages INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

-- Comentarios
COMMENT ON TABLE sessions IS 'Tracking de sesiones conversacionales';


-- ============================================================================
-- POLÍTICAS DE SEGURIDAD (Row Level Security)
-- ============================================================================
-- Supabase requiere políticas de seguridad para acceder a las tablas
-- Por ahora, permitimos acceso completo (en producción, deberías restringir)

-- Habilitar RLS
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Política: Permitir todo (SOLO PARA DESARROLLO)
-- En producción, deberías crear políticas más restrictivas

CREATE POLICY "Allow all access to logs" ON logs
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all access to users" ON users
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all access to sessions" ON sessions
    FOR ALL USING (true) WITH CHECK (true);


-- ============================================================================
-- DATOS DE PRUEBA (OPCIONAL)
-- ============================================================================
-- Inserta algunos datos de ejemplo para testing

-- Usuario de prueba
INSERT INTO users (id, username, email, full_name, role)
VALUES (101, 'docente_prueba', 'docente@example.com', 'Profesor Demo', 'teacher')
ON CONFLICT (id) DO NOTHING;

-- Log de prueba
INSERT INTO logs (user_id, session_id, user_message, bot_response, response_time_ms)
VALUES (
    101,
    'session_inicial',
    '¿Cuáles son las unidades del curso?',
    'El curso tiene 4 unidades: República Aristocrática, Oncenio de Leguía, Crisis de 1930, y Gobiernos Militares.',
    150.5
)
ON CONFLICT DO NOTHING;


-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================
-- Queries para verificar que todo se creó correctamente

-- Ver todas las tablas creadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('logs', 'users', 'sessions');

-- Contar registros en cada tabla
SELECT 'logs' as table_name, COUNT(*) as count FROM logs
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'sessions', COUNT(*) FROM sessions;


-- ============================================================================
-- SCRIPT COMPLETADO
-- ============================================================================
-- Si todo salió bien, deberías ver:
-- - 3 tablas creadas (logs, users, sessions)
-- - Índices creados
-- - Políticas de seguridad habilitadas
-- - 1 usuario de prueba (ID: 101)
-- - 1 log de prueba
-- 
-- ¡Ahora puedes ejecutar main_v3_postgres.py!
-- ============================================================================
