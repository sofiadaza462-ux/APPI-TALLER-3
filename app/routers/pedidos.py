
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from app.database import conectar
from app.schemas import PedidoCrear


router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("", status_code=201)
def crear(datos: PedidoCrear):
    # Evitar que el mismo producto aparezca dos veces.
    if len({i.producto_id for i in datos.items}) != len(datos.items):
        raise HTTPException(
            422,
            "No repita el mismo producto en un pedido"
        )

    with conectar() as db:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id FROM clientes WHERE id = %s",
                (datos.cliente_id,)
            )

            if cur.fetchone() is None:
                raise HTTPException(404, "Cliente no encontrado")

            items = sorted(datos.items, key=lambda x: x.producto_id)
            detalles = []
            total = Decimal("0.00")

            # Revisar el inventario antes de crear el pedido.
            for item in items:
                cur.execute(
                    """
                    SELECT id, precio, stock
                    FROM productos
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (item.producto_id,)
                )
                producto = cur.fetchone()

                if producto is None:
                    raise HTTPException(
                        404,
                        f"Producto {item.producto_id} no encontrado"
                    )

                if producto["stock"] < item.cantidad:
                    raise HTTPException(
                        409,
                        f"Stock insuficiente del producto {item.producto_id}"
                    )

                subtotal = producto["precio"] * item.cantidad
                total += subtotal

                detalles.append((
                    item.producto_id,
                    item.cantidad,
                    producto["precio"],
                    subtotal
                ))

            # El pedido comienza pendiente.
            cur.execute(
                """
                INSERT INTO pedidos (cliente_id, estado, total)
                VALUES (%s, 'pendiente', %s)
                """,
                (datos.cliente_id, total)
            )
            pedido_id = cur.lastrowid

            for producto_id, cantidad, precio, subtotal in detalles:
                cur.execute(
                    """
                    INSERT INTO detalle_pedidos
                    (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (pedido_id, producto_id, cantidad, precio, subtotal)
                )

                # Reservar las unidades descontándolas del inventario.
                cur.execute(
                    """
                    UPDATE productos
                    SET stock = stock - %s
                    WHERE id = %s
                    """,
                    (cantidad, producto_id)
                )

            return {
                "id": pedido_id,
                "cliente_id": datos.cliente_id,
                "estado": "pendiente",
                "total": str(total),
                "items": len(detalles)
            }


@router.get("")
def listar():
    with conectar() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT p.id, p.fecha, p.estado, p.total,
                       c.nombre AS cliente
                FROM pedidos p
                JOIN clientes c ON c.id = p.cliente_id
                ORDER BY p.fecha DESC, p.id DESC
                """
            )
            return cur.fetchall()


@router.get("/{pedido_id}")
def detalle(pedido_id: int):
    with conectar() as db:
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT p.id, p.fecha, p.estado, p.total,
                       c.nombre AS cliente
                FROM pedidos p
                JOIN clientes c ON c.id = p.cliente_id
                WHERE p.id = %s
                """,
                (pedido_id,)
            )
            pedido = cur.fetchone()

            if pedido is None:
                raise HTTPException(404, "Pedido no encontrado")

            cur.execute(
                """
                SELECT d.producto_id, pr.nombre AS producto,
                       d.cantidad, d.precio_unitario, d.subtotal
                FROM detalle_pedidos d
                JOIN productos pr ON pr.id = d.producto_id
                WHERE d.pedido_id = %s
                ORDER BY d.id
                """,
                (pedido_id,)
            )
            pedido["items"] = cur.fetchall()

            return pedido


@router.patch("/{pedido_id}/estado")
def cambiar_estado(pedido_id: int, estado: str):
    # Esta ruta confirma pedidos pendientes.
    # La cancelación debe realizarse en la ruta especial.
    if estado != "confirmado":
        raise HTTPException(
            422,
            "Solo se permite confirmar pedidos desde esta ruta. "
            "Use la ruta de cancelación para cancelar."
        )

    with conectar() as db:
        with db.cursor() as cur:
            cur.execute(
                "SELECT estado FROM pedidos WHERE id = %s FOR UPDATE",
                (pedido_id,)
            )
            pedido = cur.fetchone()

            if pedido is None:
                raise HTTPException(404, "Pedido no encontrado")

            if pedido["estado"] != "pendiente":
                raise HTTPException(
                    409,
                    "Solo se pueden confirmar pedidos pendientes"
                )

            cur.execute(
                """
                UPDATE pedidos
                SET estado = 'confirmado'
                WHERE id = %s
                """,
                (pedido_id,)
            )

            return {
                "id": pedido_id,
                "estado": "confirmado",
                "mensaje": "Pedido confirmado correctamente"
            }


@router.post("/{pedido_id}/cancelar")
def cancelar(pedido_id: int):
    with conectar() as db:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, estado FROM pedidos WHERE id = %s FOR UPDATE",
                (pedido_id,)
            )
            pedido = cur.fetchone()

            if pedido is None:
                raise HTTPException(404, "Pedido no encontrado")

            if pedido["estado"] == "cancelado":
                raise HTTPException(409, "El pedido ya está cancelado")

            # Recuperar los productos y cantidades del pedido.
            cur.execute(
                """
                SELECT producto_id, cantidad
                FROM detalle_pedidos
                WHERE pedido_id = %s
                ORDER BY producto_id
                """,
                (pedido_id,)
            )
            detalles = cur.fetchall()

            # Bloquear los productos y devolver las unidades.
            for detalle in detalles:
                cur.execute(
                    "SELECT id FROM productos WHERE id = %s FOR UPDATE",
                    (detalle["producto_id"],)
                )

                if cur.fetchone() is None:
                    raise HTTPException(
                        409,
                        "No se puede devolver el inventario de un producto inexistente"
                    )

                cur.execute(
                    """
                    UPDATE productos
                    SET stock = stock + %s
                    WHERE id = %s
                    """,
                    (detalle["cantidad"], detalle["producto_id"])
                )

            cur.execute(
                """
                UPDATE pedidos
                SET estado = 'cancelado'
                WHERE id = %s
                """,
                (pedido_id,)
            )

            return {
                "id": pedido_id,
                "estado": "cancelado",
                "mensaje": "Pedido cancelado y stock devuelto"
            }
