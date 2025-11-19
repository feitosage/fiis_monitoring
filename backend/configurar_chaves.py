#!/usr/bin/env python3
"""
Script interativo para configurar as chaves de API - Versão Backend
"""
import sys
from pathlib import Path

# Importa o script principal da raiz
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from configurar_chaves import main
    main()
except ImportError:
    print("❌ Erro: Execute o script da raiz do projeto:")
    print("   python configurar_chaves.py")
    sys.exit(1)

