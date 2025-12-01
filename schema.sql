-- Script DDL para PDV Web - MVP
-- Criado automaticamente baseado nos modelos SQLAlchemy

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    senha_hash VARCHAR NOT NULL,
    perfil VARCHAR NOT NULL CHECK (perfil IN ('vendedor', 'gerente')),
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para tabela usuarios
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_id ON usuarios(id);

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR NOT NULL,
    codigo_barras VARCHAR UNIQUE,
    preco DECIMAL(10,2) NOT NULL CHECK (preco >= 0),
    estoque DECIMAL(10,2) DEFAULT 0.0 CHECK (estoque >= 0),
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para tabela produtos
CREATE INDEX IF NOT EXISTS idx_produtos_codigo_barras ON produtos(codigo_barras);
CREATE INDEX IF NOT EXISTS idx_produtos_id ON produtos(id);

-- Tabela de vendas
CREATE TABLE IF NOT EXISTS vendas (
    id SERIAL PRIMARY KEY,
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    total DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    metodo_pagamento VARCHAR NOT NULL CHECK (metodo_pagamento IN ('dinheiro', 'cartao', 'pix')),
    status VARCHAR DEFAULT 'finalizada' CHECK (status IN ('finalizada', 'cancelada'))
);

-- Índices para tabela vendas
CREATE INDEX IF NOT EXISTS idx_vendas_usuario_id ON vendas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_vendas_data_hora ON vendas(data_hora);
CREATE INDEX IF NOT EXISTS idx_vendas_id ON vendas(id);

-- Tabela de itens de venda
CREATE TABLE IF NOT EXISTS itens_venda (
    id SERIAL PRIMARY KEY,
    venda_id INTEGER NOT NULL REFERENCES vendas(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    quantidade DECIMAL(10,2) NOT NULL CHECK (quantidade > 0),
    preco_unitario DECIMAL(10,2) NOT NULL CHECK (preco_unitario >= 0),
    subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal >= 0)
);

-- Índices para tabela itens_venda
CREATE INDEX IF NOT EXISTS idx_itens_venda_venda_id ON itens_venda(venda_id);
CREATE INDEX IF NOT EXISTS idx_itens_venda_produto_id ON itens_venda(produto_id);
CREATE INDEX IF NOT EXISTS idx_itens_venda_id ON itens_venda(id);

-- Function para atualizar o campo atualizado_em automaticamente
CREATE OR REPLACE FUNCTION update_atualizado_em()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualizar automaticamente o campo atualizado_em
CREATE TRIGGER trigger_update_usuarios_atualizado_em
    BEFORE UPDATE ON usuarios
    FOR EACH ROW
    EXECUTE FUNCTION update_atualizado_em();

CREATE TRIGGER trigger_update_produtos_atualizado_em
    BEFORE UPDATE ON produtos
    FOR EACH ROW
    EXECUTE FUNCTION update_atualizado_em();

-- Comentários nas tabelas
COMMENT ON TABLE usuarios IS 'Tabela de usuários do sistema (vendedores e gerentes)';
COMMENT ON TABLE produtos IS 'Tabela de produtos disponíveis para venda';
COMMENT ON TABLE vendas IS 'Tabela de vendas realizadas';
COMMENT ON TABLE itens_venda IS 'Tabela de itens de cada venda';

-- Comentários nas colunas importantes
COMMENT ON COLUMN usuarios.perfil IS 'Perfil do usuário: vendedor ou gerente';
COMMENT ON COLUMN vendas.metodo_pagamento IS 'Método de pagamento: dinheiro, cartao ou pix';
COMMENT ON COLUMN vendas.status IS 'Status da venda: finalizada ou cancelada';
COMMENT ON COLUMN produtos.estoque IS 'Quantidade em estoque (pode ser fracionária)';

