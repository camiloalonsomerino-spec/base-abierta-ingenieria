/*********************************************
 * Unidad 10 · Caso integrador · la mezcla de cinco prendas (el primal)
 * El modelo de la unidad 4; acá se leen los .dual de las tres capacidades y de
 * las cinco demandas máximas. Datos en u10_mezcla.dat.
 *********************************************/
{string} Prendas  = ...;
{string} Recursos = ...;
float margen[Prendas]        = ...;
float uso[Recursos][Prendas] = ...;
float cap[Recursos]          = ...;
float demanda[Prendas]       = ...;

dvar float+ x[Prendas];

maximize sum(i in Prendas) margen[i] * x[i];

subject to {
  forall(r in Recursos)
    Capacidad: sum(i in Prendas) uso[r][i] * x[i] <= cap[r];
  forall(i in Prendas)
    Demanda: x[i] <= demanda[i];
}

execute {
  for (var r in Recursos)
    writeln("y_", r, " = ", Capacidad[r].dual);
  for (var i in Prendas)
    writeln("u_", i, " = ", Demanda[i].dual);
}
