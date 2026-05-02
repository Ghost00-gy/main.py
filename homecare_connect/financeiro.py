class FinanceService:
    @staticmethod
    def calcular_split(valor_total: float, categoria: str):
        # Regras de negócio baseadas no mercado brasileiro
        taxas = {
            "Médico": 0.15,
            "Enfermeiro": 0.12,
            "Fisioterapeuta": 0.12,
            "Técnico": 0.10
        }
        percentual = taxas.get(categoria, 0.12)
        
        taxa_adm = valor_total * percentual
        repasse_profissional = valor_total - taxa_adm
        
        return {
            "total_pago_pelo_paciente": valor_total,
            "comissao_homecare_connect": taxa_adm,
            "liquido_profissional": repasse_profissional
        }
