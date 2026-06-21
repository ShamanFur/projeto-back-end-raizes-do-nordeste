from datetime import datetime
import random

def processar_pagamento(pedido_id: int, valor: float, forma_pagamento: str ) -> dict:
    aprovado = random.random() > 0.2 #simula 80% de aprovação e os outros 20% de recusa, esse resultado viria da API externa tipo um pagseguro

    return{
        "transacao_id": f"Mock-{pedido_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "pedido_id":pedido_id, "valor": valor,
        "forma_pagamento": forma_pagamento,
        "status": "Aprovado" if aprovado else "Recusado",
        "mensagem":"Pagamento aprovado!!!" if aprovado else "Pagamento recusado, tente novamente. ",
        "feito_em": datetime.utcnow().isoformat()
    }