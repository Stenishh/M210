@echo off
chcp 65001 > nul
title Calculadora Simplex

echo ========================================
echo  🧮 Calculadora Simplex - Iniciando...
echo ========================================
echo.

if not exist ".venv" (
    echo ❌ Ambiente virtual não encontrado!
    echo 💡 Criando ambiente virtual...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo 📦 Instalando dependências...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo ⚙️  Iniciando aplicação...
echo 🌐 A aplicação abrirá automaticamente no navegador.
echo.
streamlit run calculadora_simplex.py

pause

