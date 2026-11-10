"""
Captura diária das intimações (roda sozinho, sem abrir o app).
Uso manual:  python capturar.py          (olha os últimos dias definidos nas Configurações)
             python capturar.py 30       (olha os últimos 30 dias)
O agendar_captura.bat cadastra este script no Agendador de Tarefas do Windows para rodar todo dia.
Se houver token em .streamlit/secrets.toml, o resultado também vai para a cópia online.
"""
import sys

import nucleo as nc

erro = nc.ativar_nuvem(nc.segredos_locais())
if erro:
    print("AVISO (cópia online):", erro)
if nc.NUVEM:
    nc.NUVEM.puxar()
banco = nc.ler_dados()
if not banco["config"].get("oabs") and not banco["config"].get("parceiros"):
    print("Cadastre o número da sua OAB no app (Configurações) antes de rodar a captura.")
    sys.exit(1)
dias = int(sys.argv[1]) if len(sys.argv) > 1 else None
novas, erros = nc.capturar(banco, dias=dias)
erro = nc.gravar_dados(banco)
print(f"{banco['ultima_busca']} · {novas} intimação(ões) nova(s)")
for e in erros + ([erro] if erro else []):
    print("ERRO:", e)
