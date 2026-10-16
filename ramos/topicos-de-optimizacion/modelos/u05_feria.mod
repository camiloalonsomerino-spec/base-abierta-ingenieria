/*********************************************
 * Unidad 5 · Ejemplo resuelto
 * Feria navideña: qué cajas de productos llevar en el maletero (mochila binaria)
 * Datos en u05_feria.dat. Base abierta de ingeniería.
 *********************************************/

{string} Productos = ...;

float ganancia[Productos] = ...;   // miles de pesos por caja vendida en la feria
float litros[Productos]   = ...;   // volumen de cada caja
float maletero            = ...;   // litros disponibles

dvar boolean x[Productos];         // 1 si se lleva la caja del producto; 0 en otro caso

dexpr float Ganancia = sum(p in Productos) ganancia[p] * x[p];

maximize Ganancia;

subject to {
  Maletero:
    sum(p in Productos) litros[p] * x[p] <= maletero;
}

execute {
  writeln("ganancia = ", Ganancia);
  for (var p in Productos) writeln("x[", p, "] = ", x[p]);
}
