/*********************************************
 * Unidad 6 · caso integrador Estampa Sur
 * ε-restricción: el mayor margen de la semana usando a lo más `eps` gramos de
 * tinta. Cambiando `eps` en el .dat se recorre la frontera margen-tinta; el
 * precio sombra de la tinta es la pendiente de la frontera en ese tramo.
 * Datos en u06_estampa_epsilon.dat (cifras del script del caso).
 * Base abierta de ingeniería.
 *********************************************/

{string} Prendas = ...;
float margen[Prendas]  = ...;   // $ por unidad
float est[Prendas]     = ...;   // segundos de estampado por unidad
float pla[Prendas]     = ...;   // segundos de planchado por unidad
float tinta[Prendas]   = ...;   // gramos por unidad
float demanda[Prendas] = ...;   // unidades por semana
float capEst = ...;             // segundos de estampado en la semana
float capPla = ...;             // segundos de planchado en la semana
float eps    = ...;             // gramos de tinta permitidos

dvar float+ x[Prendas];

dexpr float Margen = sum(p in Prendas) margen[p] * x[p];
dexpr float Tinta  = sum(p in Prendas) tinta[p] * x[p];

maximize Margen;

subject to {
  Estampado: sum(p in Prendas) est[p] * x[p] <= capEst;
  Planchado: sum(p in Prendas) pla[p] * x[p] <= capPla;
  Tope:      Tinta <= eps;
  forall(p in Prendas) Demanda: x[p] <= demanda[p];
}

execute {
  writeln("margen = ", Margen);
  writeln("tinta = ", Tinta);
  writeln("dual_tinta = ", Tope.dual);
  for (var p in Prendas) writeln("x[", p, "] = ", x[p]);
}
