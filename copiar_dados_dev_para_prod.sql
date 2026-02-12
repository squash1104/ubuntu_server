-- Script para copiar dados do banco sisvot_dev_db para sisvot_db
-- Execute como postgres no servidor

-- ===========================================
-- COPIAR USUÁRIOS (auth_user)
-- ===========================================
INSERT INTO sisvot_db.public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
SELECT id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined
FROM sisvot_dev_db.public.auth_user
ON CONFLICT (id) DO UPDATE SET
    password = EXCLUDED.password,
    last_login = EXCLUDED.last_login,
    is_superuser = EXCLUDED.is_superuser,
    username = EXCLUDED.username,
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    is_staff = EXCLUDED.is_staff,
    is_active = EXCLUDED.is_active,
    date_joined = EXCLUDED.date_joined;

-- ===========================================
-- COPIAR COLABORADORES
-- ===========================================
INSERT INTO sisvot_db.public.colaboradores (id, nome, telefone, data_nascimento, cidade_id, bairro_id, tipo, data_cadastro, cadastrado_por_id)
SELECT id, nome, telefone, data_nascimento, cidade_id, bairro_id, tipo, data_cadastro, cadastrado_por_id
FROM sisvot_dev_db.public.colaboradores
ON CONFLICT (id) DO UPDATE SET
    nome = EXCLUDED.nome,
    telefone = EXCLUDED.telefone,
    data_nascimento = EXCLUDED.data_nascimento,
    cidade_id = EXCLUDED.cidade_id,
    bairro_id = EXCLUDED.bairro_id,
    tipo = EXCLUDED.tipo,
    data_cadastro = EXCLUDED.data_cadastro,
    cadastrado_por_id = EXCLUDED.cadastrado_por_id;

-- ===========================================
-- COPIAR CONVIDADOS
-- ===========================================
INSERT INTO sisvot_db.public.convidados (id, nome, telefone, data_nascimento, cidade_id, bairro_id, colaborador_id, data_cadastro, cadastrado_por_id)
SELECT id, nome, telefone, data_nascimento, cidade_id, bairro_id, colaborador_id, data_cadastro, cadastrado_por_id
FROM sisvot_dev_db.public.convidados
ON CONFLICT (id) DO UPDATE SET
    nome = EXCLUDED.nome,
    telefone = EXCLUDED.telefone,
    data_nascimento = EXCLUDED.data_nascimento,
    cidade_id = EXCLUDED.cidade_id,
    bairro_id = EXCLUDED.bairro_id,
    colaborador_id = EXCLUDED.colaborador_id,
    data_cadastro = EXCLUDED.data_cadastro,
    cadastrado_por_id = EXCLUDED.cadastrado_por_id;

-- ===========================================
-- COPIAR HISTÓRICO
-- ===========================================
INSERT INTO sisvot_db.public.historico_historico (id, data_hora, acao, usuario_id, detalhes, ip_address)
SELECT id, data_hora, acao, usuario_id, detalhes, ip_address
FROM sisvot_dev_db.public.historico_historico
ON CONFLICT (id) DO UPDATE SET
    data_hora = EXCLUDED.data_hora,
    acao = EXCLUDED.acao,
    usuario_id = EXCLUDED.usuario_id,
    detalhes = EXCLUDED.detalhes,
    ip_address = EXCLUDED.ip_address;

-- ===========================================
-- COPIAR MENSAGENS (se existir)
-- ===========================================
-- Descomente se houver tabelas de mensagens
-- INSERT INTO sisvot_db.public.mensagens_...
-- SELECT ... FROM sisvot_dev_db.public.mensagens_...

-- Verificar quantidade de registros copiados:
-- SELECT 'Usuários' as tabela, count(*) as total FROM sisvot_db.public.auth_user
-- UNION ALL SELECT 'Colaboradores', count(*) FROM sisvot_db.public.colaboradores
-- UNION ALL SELECT 'Convidados', count(*) FROM sisvot_db.public.convidados;
