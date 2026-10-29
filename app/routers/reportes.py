
from fastapi import APIRouter

from app.database import conectar


router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/ventas-por-cliente")
def ventas_por_cliente():
    with conectar() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id AS cliente_id,
                    c.nombre AS cliente,
                    COUNT(p.id) AS cantidad_pedidos,
                    COALESCE(SUM(p.total), 0) AS total_ventas
                FROM clientes c
                LEFT JOIN pedidos p
                    ON p.cliente_id = c.id
                    AND p.estado = 'confirmado'
                GROUP BY c.id, c.nombre
                ORDER BY total_ventas DESC, c.nombre ASC
                """
            )
            return cur.fetchall()
