from fastapi import FastAPI, Depends, HTTPException
from app.models import Base
from app.services.financeiro import FinanceService
from sqlalchemy.orm import Session

app = FastAPI(title="HomeCare Connect API", version="1.0.0")

@app.get("/")
def home():
    return {"status": "HomeCare Connect operando em nível nacional"}

@app.post("/atendimentos/orcamento")
async def gerar_orcamento(categoria: str, horas: int):
    # Valores base de mercado
    tabela = {"Médico": 250, "Enfermeiro": 120, "Técnico": 70}
    valor_base = tabela.get(categoria, 50) * horas
    
    # Aplica o split automaticamente
    orcamento = FinanceService.calcular_split(valor_base, categoria)
    return orcamento

@app.get("/especialistas/busca")
async def buscar_especialistas(cidade: str, uf: str, categoria: str):
    # Lógica de geolocalização e filtro de banco de dados
    return {"mensagem": f"Buscando {categoria} em {cidade}-{uf}"}
