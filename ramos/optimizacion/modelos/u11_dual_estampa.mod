/*********************************************
 * Unidad 11 · Holgura complementaria
 * Estampa Sur: el DUAL de la mezcla semanal de la unidad 4.
 * y[r]  = valor de un segundo (o gramo) más del recurso r
 * u[i]  = valor de subir en una unidad el tope de demanda de la prenda i
 * Cada prenda pone una restricción: lo que valen sus recursos más su tope
 * tiene que cubrir su margen. Las duales de estas restricciones devuelven
 * la mezcla óptima del primal (x_desde_dual).
 * Datos en u11_dual_estampa.dat (las mismas cifras que el caso integrador).
 *********************************************/

{string} Prendas  = ...;
{string} Recursos = ...;

float margen[Prendas]         = ...;
float uso[Recursos][Prendas]  = ...;
float cap[Recursos]           = ...;
float demanda[Prendas]        = ...;

dvar float+ y[Recursos];
dvar float+ u[Prendas];

dexpr float W = sum(r in Recursos) cap[r] * y[r] + sum(i in Prendas) demanda[i] * u[i];

minimize W;

subject to {
  forall(i in Prendas)
    Cubre:
      sum(r in Recursos) uso[r][i] * y[r] + u[i] >= margen[i];
}

execute {
  writeln("w = ", W);
  for (var r in Recursos) writeln("y[", r, "] = ", y[r]);
  for (var i in Prendas) {
    writeln("u[", i, "] = ", u[i]);
    writeln("holgura_dual[", i, "] = ", Cubre[i].slack);
    writeln("x_desde_dual[", i, "] = ", Cubre[i].dual);
  }
}
