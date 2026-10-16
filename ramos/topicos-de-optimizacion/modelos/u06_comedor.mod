/*********************************************
 * Unidad 6 · Ejemplo resuelto
 * Comedor solidario: sacos de legumbres y cajas de verduras al menor costo
 * Base abierta de ingeniería.
 *********************************************/

dvar int+ sacos;     // sacos de legumbres que se compran en la semana
dvar int+ cajas;     // cajas de verduras que se compran en la semana

minimize 7 * sacos + 8 * cajas;           // miles de pesos

subject to {
  Proteina: 6 * sacos + 1 * cajas >= 28;  // raciones de proteína
  Fibra:    3 * sacos + 4 * cajas >= 27;  // raciones de fibra
}

execute {
  writeln("sacos = ", sacos);
  writeln("cajas = ", cajas);
}
