/*********************************************
 * Unidad 5 · Ejercicio 5.10
 * Imprenta: qué pedidos aceptar para el fin de semana (mochila binaria)
 * Datos en u05_e10_imprenta.dat. Base abierta de ingeniería.
 *********************************************/

int n = ...;
range Pedidos = 1..n;

float margen[Pedidos] = ...;   // miles de pesos
float horas[Pedidos]  = ...;   // horas-máquina
float H               = ...;   // horas-máquina del fin de semana

dvar boolean x[Pedidos];       // 1 si se acepta el pedido j; 0 en otro caso

maximize sum(j in Pedidos) margen[j] * x[j];

subject to {
  Horas:
    sum(j in Pedidos) horas[j] * x[j] <= H;
}

execute {
  for (var j in Pedidos) writeln("x[", j, "] = ", x[j]);
}
