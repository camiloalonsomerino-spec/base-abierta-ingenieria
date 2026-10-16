/*********************************************
 * Unidad 4 · Caso integrador · Estampa Sur decide su mezcla semanal
 * Cinco prendas compiten por tres recursos: estampado, planchado (en segundos) y tinta (en gramos).
 * Datos en u04_mezcla.dat. Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS
{string} Prendas  = ...;
{string} Recursos = ...;

// PARÁMETROS
float margen[Prendas]        = ...;   // CLP por unidad
float uso[Recursos][Prendas] = ...;   // segundos o gramos por unidad
float cap[Recursos]          = ...;   // segundos o gramos por semana
float demanda[Prendas]       = ...;   // unidades por semana, máximo

// VARIABLES
dvar float+ x[Prendas];               // unidades a producir en la semana

// EXPRESIONES
dexpr float Margen = sum(i in Prendas) margen[i] * x[i];
dexpr float usado[r in Recursos] = sum(i in Prendas) uso[r][i] * x[i];

maximize Margen;

subject to {
  forall(r in Recursos)
    Capacidad: usado[r] <= cap[r];

  forall(i in Prendas)
    Demanda: x[i] <= demanda[i];
}

execute {
  writeln("margen = ", Margen);
  for (var i in Prendas)
    writeln("x_", i, " = ", x[i]);
  for (var r in Recursos) {
    writeln("holgura_", r, " = ", Capacidad[r].slack);
    writeln("dual_", r, " = ", Capacidad[r].dual);
  }
  for (var i in Prendas)
    writeln("dual_demanda_", i, " = ", Demanda[i].dual);
}
