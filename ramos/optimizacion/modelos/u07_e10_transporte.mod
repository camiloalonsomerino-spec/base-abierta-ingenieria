/*********************************************
 * Unidad 7 · Ejercicio 7.10 (pauta)
 * Distribuidora: cajas desde tres bodegas a cuatro locales
 *********************************************/

{string} Bodegas = ...;
{string} Locales = ...;

float oferta[Bodegas]             = ...;   // cajas disponibles por semana
float pedido[Locales]             = ...;   // cajas que pide cada local
float costo[Bodegas][Locales]     = ...;   // CLP por caja enviada

dvar float+ x[Bodegas][Locales];           // cajas de la bodega b al local l

minimize sum(b in Bodegas, l in Locales) costo[b][l] * x[b][l];

subject to {
  forall(b in Bodegas)
    Oferta:
      sum(l in Locales) x[b][l] <= oferta[b];
  forall(l in Locales)
    Pedido:
      sum(b in Bodegas) x[b][l] >= pedido[l];
}

execute {
  writeln("costo = ", cplex.getObjValue());
  for (var b in Bodegas)
    for (var l in Locales)
      if (x[b][l] > 0)
        writeln("x[", b, "][", l, "] = ", x[b][l]);
  for (var b in Bodegas) {
    writeln("holgura[", b, "] = ", Oferta[b].slack);
    writeln("dual_oferta[", b, "] = ", Oferta[b].dual);
  }
  for (var l in Locales)
    writeln("dual_pedido[", l, "] = ", Pedido[l].dual);
  for (var b in Bodegas)
    for (var l in Locales)
      writeln("cr[", b, "][", l, "] = ", x[b][l].reducedCost);
}
