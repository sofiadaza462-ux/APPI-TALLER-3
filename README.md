# Taller 3 ADSO - Tienda

## 1. Descripción

Este proyecto es una API creada con Python, FastAPI y MySQL para administrar los clientes, productos y pedidos de una tienda.

## 2. Objetivo

Organizar la información de los clientes, registrar productos, crear pedidos, controlar las existencias y consultar las ventas de la tienda.

## 3. Herramientas utilizadas

- **Python:** para crear el programa.
- **FastAPI:** para recibir y responder solicitudes.
- **MySQL:** para guardar la información.
- **Visual Studio Code:** para escribir el código.

## 4. Organización del proyecto

- `main.py`: inicia el programa y conecta sus funciones.
- `database.py`: conecta el programa con MySQL.
- `schemas.py`: revisa que los datos sean correctos.
- `clientes.py`: permite registrar, consultar, actualizar y eliminar clientes.
- `productos.py`: permite registrar, buscar, consultar y actualizar productos.
- `pedidos.py`: permite crear, consultar, confirmar y cancelar pedidos.
- `reportes.py`: muestra un resumen de las ventas por cliente.
- `01_esquema.sql`: crea las tablas de la base de datos.
- `02_datos_prueba.sql`: agrega clientes y productos iniciales.

## 5. Base de datos

La base de datos se llama `tienda_adso` y contiene cuatro tablas:

- **clientes:** guarda los datos de los clientes.
- **productos:** guarda los productos, sus precios y existencias.
- **pedidos:** guarda los pedidos, sus fechas, estados y valores totales.
- **detalle_pedidos:** guarda los productos incluidos en cada pedido, sus cantidades y precios.

## 6. Funciones del programa

El programa permite:

- Registrar y consultar clientes.
- Consultar los pedidos realizados por cada cliente.
- Actualizar y eliminar clientes según las reglas del programa.
- Registrar, buscar y consultar productos.
- Actualizar las existencias de los productos.
- Crear pedidos y calcular su valor total.
- Descontar del inventario los productos de cada pedido.
- Confirmar pedidos pendientes.
- Cancelar pedidos y devolver los productos al inventario.
- Consultar los pedidos y sus detalles.
- Generar un reporte de ventas por cliente.

## 7. Reglas del programa

- El precio de un producto debe ser mayor que cero.
- Las existencias no pueden ser negativas.
- El cliente debe estar registrado para realizar un pedido.
- Debe haber suficientes productos disponibles.
- Cada pedido debe incluir al menos un producto.
- No se puede eliminar un cliente que tenga pedidos registrados.
- No se puede cancelar dos veces el mismo pedido.
- Los pedidos cancelados no se pueden volver a confirmar.
- El reporte de ventas cuenta únicamente los pedidos confirmados.

## 8. Estados de los pedidos

Los pedidos pueden tener tres estados:

- **Pendiente:** el pedido fue creado y sus productos se descontaron del inventario.
- **Confirmado:** el pedido fue confirmado.
- **Cancelado:** el pedido fue cancelado y las unidades se devolvieron al inventario.

Los cambios permitidos son:

- Pendiente a confirmado.
- Pendiente a cancelado.
- Confirmado a cancelado.

Un pedido cancelado no puede volver a confirmarse ni cancelarse otra vez.

## 9. Instalación

Primero, se debe tener Python y MySQL instalados.

Crear el entorno virtual:

```bash
python -m venv .venv
```

Activarlo en Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las librerías:

```bash
pip install -r requirements.txt
```

Configurar el archivo `.env` con los datos de conexión a MySQL.

Después, ejecutar los archivos SQL en este orden:

1. `sql/01_esquema.sql`
2. `sql/02_datos_prueba.sql`

El segundo archivo debe ejecutarse una sola vez para evitar duplicar los datos iniciales.

## 10. Ejecutar el programa

Desde la terminal, ejecutar:

```bash
fastapi dev app/main.py
```

Para abrir el programa:

http://127.0.0.1:8000/

Para consultar las funciones disponibles:

http://127.0.0.1:8000/docs

## 11. Estándares de codificación

El código está organizado en diferentes archivos, utiliza nombres claros y mantiene una sangría ordenada. También incluye validaciones para evitar datos incorrectos y funciones separadas para administrar clientes, productos, pedidos y reportes.

## 12. Reporte de ventas

La ruta `GET /reportes/ventas-por-cliente` muestra los clientes, la cantidad de pedidos confirmados y el total de sus ventas confirmadas. Esta función consulta la información sin modificar los registros.

## 13. Conclusión

Este proyecto permite administrar clientes, productos y pedidos de una tienda. También permite controlar las existencias, gestionar la cancelación de pedidos y consultar las ventas por cliente mediante Python, FastAPI y MySQL.