#!/bin/bash

# 📊 Calculadora Simplex - Script de Inicialização (macOS/Linux)
# Criado por: Stenishh
# GitHub: https://github.com/Stenishh/M210

echo "🚀 Iniciando Calculadora Simplex..."
echo "📊 Programação Linear com Método Simplex"
echo "----------------------------------------"

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "💡 Instale o Python 3.8+ primeiro:"
    echo "   👉 https://www.python.org/downloads/"
    exit 1
fi

# Verifica versão do Python
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python $PYTHON_VERSION detectado"

# Verifica se pip está disponível
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado!"
    echo "💡 Instale o pip primeiro."
    exit 1
fi

# Cria ambiente virtual se não existir
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv .venv
    
    
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao criar ambiente virtual!"
        echo "💡 Verifique se o módulo venv está instalado:"
        echo "   👉 python3 -m pip install --user virtualenv"
        exit 1
    fi
    
    echo "✅ Ambiente virtual criado com sucesso!"
else
    echo "📦 Ambiente virtual já existe"
fi

# Ativa o ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source .venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Erro ao ativar ambiente virtual!"
    exit 1
fi

echo "✅ Ambiente virtual ativado"

# Atualiza pip
echo "🔄 Atualizando pip..."
pip install --upgrade pip --quiet

# Verifica se requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "❌ Arquivo requirements.txt não encontrado!"
    echo "💡 Certifique-se de estar no diretório correto do projeto."
    exit 1
fi

# Instala dependências
echo "📥 Instalando dependências..."
echo "   📋 Lendo requirements.txt..."

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências!"
    echo "💡 Verifique sua conexão com a internet e tente novamente."
    exit 1
fi

echo "✅ Dependências instaladas com sucesso!"

# Verifica se o arquivo principal existe
if [ ! -f "calculadora_simplex.py" ]; then
    echo "❌ Arquivo calculadora_simplex.py não encontrado!"
    echo "💡 Certifique-se de estar no diretório correto do projeto."
    exit 1
fi

# Inicia a aplicação
echo ""
echo "🌐 Iniciando aplicação Streamlit..."
echo "🔗 URL: http://localhost:8501"
echo "⚠️  Para parar a aplicação, pressione Ctrl+C"
echo ""
echo "----------------------------------------"
echo "📊 Calculadora Simplex - Pronta para uso!"
echo "----------------------------------------"

# Executa o Streamlit
streamlit run calculadora_simplex.py

# Verifica se houve erro na execução
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erro ao executar a aplicação!"
    echo "💡 Verifique se todas as dependências foram instaladas corretamente."
    exit 1
fi

echo ""
echo "👋 Aplicação encerrada. Até logo!"