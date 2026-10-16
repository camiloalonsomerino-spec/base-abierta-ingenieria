/*********************************************
 * Unidad 10 · Caso integrador · el dual de la mezcla de cinco prendas
 * y[r]: CLP por segundo (o por gramo) del recurso r · u[i]: CLP por unidad de
 * demanda máxima de la prenda i. Datos en u10_mezcla.dat.
 *********************************************/
{string} Prendas  = ...;
{string} Recursos = ...;
float margen[Prendas]        = ...;
float uso[Recursos][Prendas] = ...;
float cap[Recursos]          = ...;
float demanda[Prendas]       = ...;

dvar float+ y[Recursos];
dvar float+ u[Prendas];

minimize sum(r in Recursos) cap[r] * y[r] + sum(i in Prendas) demanda[i] * u[i];

subject to {
  forall(i in Prendas)
    Valor: sum(r in Recursos) uso[r][i] * y[r] + u[i] >= margen[i];
}

execute {
  for (var r in Recursos)
    writeln("y_", r, " = ", y[r]);
  for (var i in Prendas) {
    writeln("u_", i, " = ", u[i]);
    writeln("x_", i, " = ", Valor[i].dual);
  }
}
