-- Unidad 5 · Caso integrador · qué acepta y qué rechaza la base de Estampa Sur
-- Se corre sobre una COPIA de datos/estampa_sur.db: el verificador la copia en memoria y la original
-- no se toca. Para repetirlo a mano: copia el archivo y abre la copia con sqlite3.
PRAGMA foreign_keys = ON;

-- @a detalle de un pedido que no existe
INSERT INTO detalle_pedido VALUES (999, 1, 10, 3990);
-- @b un tipo de cliente que no está en la lista
INSERT INTO cliente (nombre, tipo, id_tienda) VALUES ('Cliente 31', 'mayorista', 1);
-- @c un cliente de una tienda que no existe
INSERT INTO cliente (nombre, tipo, id_tienda) VALUES ('Cliente 31', 'club', 7);
-- @d un producto con un nombre que ya existe
INSERT INTO producto (nombre, precio, costo_var, seg_estampado) VALUES ('gorros', 3290, 2020, 30);
-- @e un producto con precio cero
INSERT INTO producto (nombre, precio, costo_var, seg_estampado) VALUES ('viseras', 0, 1450, 25);
-- @f la misma prenda dos veces en el mismo pedido
INSERT INTO detalle_pedido VALUES (1, 2, 12, 9890);
-- @g borrar un cliente que tiene pedidos
DELETE FROM cliente WHERE id_cliente = 1;
-- @h borrar un cliente que nunca compró
DELETE FROM cliente WHERE id_cliente = 27;
-- @i borrar un pedido que tiene detalle
DELETE FROM pedido WHERE id_pedido = 3;
-- @j una orden de producción con lote negativo
INSERT INTO orden_produccion (id_producto, semana, lote) VALUES (2, 6, -360);
-- @k una segunda orden de poleras básicas para la semana 6
INSERT INTO orden_produccion (id_producto, semana, lote) VALUES (1, 6, 720);
-- @l dos pedidos del mismo cliente el mismo día
SELECT id_pedido, id_cliente, fecha FROM pedido WHERE id_cliente = 1 AND fecha = '2026-03-17';
-- @m se apagan las claves foráneas
PRAGMA foreign_keys = OFF;
-- @n un pedido del cliente 45, que no existe
INSERT INTO pedido VALUES (121, 45, '2026-03-31', 'pendiente');
-- @o
PRAGMA foreign_key_check;
-- @p se borra ese pedido
DELETE FROM pedido WHERE id_pedido = 121;
PRAGMA foreign_keys = ON;
