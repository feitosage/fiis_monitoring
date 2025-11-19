"""
Módulo de pesquisa web para análise de FIIs
Busca informações em múltiplas fontes para enriquecer a análise de IA
"""

import requests
from bs4 import BeautifulSoup
import time
import re


class PesquisadorFII:
    """Pesquisador de informações sobre FIIs em múltiplas fontes"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.timeout = 10
    
    def pesquisar_fii(self, ticker):
        """
        Pesquisa informações sobre um FII em múltiplas fontes
        
        Args:
            ticker: Código do FII (ex: MXRF11)
        
        Returns:
            dict com informações agregadas
        """
        ticker_limpo = ticker.replace('.SA', '')
        
        print(f"\n🔍 Iniciando pesquisa sobre {ticker_limpo}...")
        
        informacoes = {
            'ticker': ticker_limpo,
            'fontes_consultadas': [],
            'resumo_geral': '',
            'noticias_recentes': [],
            'analises_encontradas': [],
            'dados_setor': '',
            'recomendacoes': []
        }
        
        # 1. Busca informações gerais via Google
        info_google = self._buscar_google(ticker_limpo)
        if info_google:
            informacoes['fontes_consultadas'].append('Google Search')
            informacoes['resumo_geral'] = info_google
        
        # 2. Tenta buscar no Fund Explorer (dados públicos)
        info_fundexplorer = self._buscar_fundexplorer(ticker_limpo)
        if info_fundexplorer:
            informacoes['fontes_consultadas'].append('Fund Explorer')
            informacoes['dados_setor'] = info_fundexplorer
        
        # 3. Busca notícias recentes
        noticias = self._buscar_noticias(ticker_limpo)
        if noticias:
            informacoes['noticias_recentes'] = noticias
        
        print(f"  ✅ Pesquisa concluída. Fontes consultadas: {', '.join(informacoes['fontes_consultadas'])}")
        
        return informacoes
    
    def _buscar_google(self, ticker):
        """Busca informações gerais via Google"""
        try:
            print(f"  📡 Buscando em: Google Search...")
            
            # Simula busca do Google (sem API)
            query = f"FII {ticker} análise 2024 2025"
            url = f"https://www.google.com/search?q={query}"
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                # Extrai snippets básicos
                soup = BeautifulSoup(response.text, 'html.parser')
                snippets = []
                
                # Procura por divs com classes de resultado do Google
                for div in soup.find_all('div', class_=re.compile('VwiC3b|yXK7lf')):
                    texto = div.get_text().strip()
                    if ticker in texto and len(texto) > 50:
                        snippets.append(texto[:200])
                        if len(snippets) >= 3:
                            break
                
                if snippets:
                    return " | ".join(snippets)
            
            print(f"    ⚠️  Google: sem resultados relevantes")
            return None
            
        except Exception as e:
            print(f"    ❌ Erro ao buscar no Google: {str(e)}")
            return None
    
    def _buscar_fundexplorer(self, ticker):
        """Busca dados no Fund Explorer (se disponível publicamente)"""
        try:
            print(f"  📡 Buscando em: Fund Explorer...")
            
            # Fund Explorer tem API pública (sem auth)
            url = f"https://www.fundsexplorer.com.br/funds/{ticker}"
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Tenta extrair informações básicas
                info = []
                
                # Procura por informações de setor
                setor_div = soup.find('div', class_=re.compile('sector|setor'))
                if setor_div:
                    info.append(f"Setor: {setor_div.get_text().strip()}")
                
                # Procura por gestora
                gestora_div = soup.find('div', class_=re.compile('manager|gestora'))
                if gestora_div:
                    info.append(f"Gestora: {gestora_div.get_text().strip()}")
                
                if info:
                    print(f"    ✅ Fund Explorer: dados encontrados")
                    return " | ".join(info)
            
            print(f"    ⚠️  Fund Explorer: sem dados")
            return None
            
        except Exception as e:
            print(f"    ❌ Erro ao buscar no Fund Explorer: {str(e)}")
            return None
    
    def _buscar_noticias(self, ticker):
        """Busca notícias recentes sobre o FII"""
        try:
            print(f"  📰 Buscando notícias recentes...")
            
            # Busca notícias via Google News
            query = f"FII {ticker} notícias"
            url = f"https://www.google.com/search?q={query}&tbm=nws"
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                noticias = []
                
                # Procura por títulos de notícias
                for div in soup.find_all('div', class_=re.compile('JheGif|nDgy9d')):
                    titulo = div.get_text().strip()
                    if titulo and len(titulo) > 20:
                        noticias.append(titulo)
                        if len(noticias) >= 3:
                            break
                
                if noticias:
                    print(f"    ✅ Encontradas {len(noticias)} notícias")
                    return noticias
            
            print(f"    ⚠️  Sem notícias recentes")
            return []
            
        except Exception as e:
            print(f"    ❌ Erro ao buscar notícias: {str(e)}")
            return []
    
    def formatar_contexto_ia(self, informacoes):
        """
        Formata as informações pesquisadas para contexto da IA
        
        Args:
            informacoes: dict com dados pesquisados
        
        Returns:
            string formatada para incluir no prompt
        """
        contexto = []
        
        if informacoes['fontes_consultadas']:
            contexto.append(f"📚 FONTES CONSULTADAS: {', '.join(informacoes['fontes_consultadas'])}")
        
        if informacoes['resumo_geral']:
            contexto.append(f"\n📖 INFORMAÇÕES GERAIS:\n{informacoes['resumo_geral']}")
        
        if informacoes['dados_setor']:
            contexto.append(f"\n🏢 DADOS DO FUNDO:\n{informacoes['dados_setor']}")
        
        if informacoes['noticias_recentes']:
            contexto.append(f"\n📰 NOTÍCIAS RECENTES:")
            for i, noticia in enumerate(informacoes['noticias_recentes'], 1):
                contexto.append(f"  {i}. {noticia}")
        
        if not contexto:
            return "\n⚠️  Nenhuma informação adicional encontrada nas pesquisas web.\n"
        
        return "\n".join(contexto)


# Instância global do pesquisador
pesquisador = PesquisadorFII()


def pesquisar_multiplos_fiis(tickers):
    """
    Pesquisa informações sobre múltiplos FIIs
    
    Args:
        tickers: lista de tickers (ex: ['MXRF11', 'HGLG11'])
    
    Returns:
        dict com informações de cada FII
    """
    resultados = {}
    
    for ticker in tickers[:5]:  # Limita a 5 FIIs para não demorar muito
        ticker_limpo = ticker.replace('.SA', '')
        
        try:
            info = pesquisador.pesquisar_fii(ticker)
            resultados[ticker_limpo] = info
            
            # Pequena pausa entre requisições para não sobrecarregar
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Erro ao pesquisar {ticker_limpo}: {str(e)}")
            resultados[ticker_limpo] = {
                'ticker': ticker_limpo,
                'erro': str(e),
                'fontes_consultadas': []
            }
    
    return resultados

