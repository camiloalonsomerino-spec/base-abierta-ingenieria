/*********************************************
 * Unidad 12 · Ejemplo resuelto · la camioneta de la feria (exacto)
 * Mochila binaria: qué cajas llevar con 14 jabas de espacio.
 * x[i] = 1 si se lleva la caja i; 0 en otro caso.
 * Datos en u12_feria_exacto.dat. Base abierta de ingeniería.
 *********************************************/

{string} Cajas = ...;
float ganancia[Cajas] = ...;            // miles de pesos
float volumen[Cajas]  = ...;            // jabas
float cap = ...;                        // jabas de la camioneta

dvar boolean x[Cajas];                  // 1 si se lleva la caja i

maximize sum(i in Cajas) ganancia[i] * x[i];

subject to {
  Espacio: sum(i in Cajas) volumen[i] * x[i] <= cap;
}

execute {
  for (var i in Cajas) writeln("x_", i, " = ", x[i]);
}
