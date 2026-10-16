/*********************************************
 * Unidad 7 · Ejercicio 7.2 (el código que se lee)
 * Alimento para perros: lote de mínimo costo
 *********************************************/

{string} Ingredientes = ...;
{string} Nutrientes   = ...;

float costo[Ingredientes]              = ...;
float aporte[Nutrientes][Ingredientes] = ...;
float minimo[Nutrientes]               = ...;
float maximo[Nutrientes]               = ...;
float K                                = ...;

dvar float+ kg[Ingredientes];

minimize sum(i in Ingredientes) costo[i] * kg[i];

subject to {
  Total:
    sum(i in Ingredientes) kg[i] == K;
  forall(n in Nutrientes)
    Piso:
      sum(i in Ingredientes) aporte[n][i] * kg[i] >= minimo[n] * K;
  forall(n in Nutrientes: maximo[n] > 0)
    Techo:
      sum(i in Ingredientes) aporte[n][i] * kg[i] <= maximo[n] * K;
}

execute {
  writeln("costo = ", cplex.getObjValue());
  for (var i in Ingredientes) {
    writeln("kg[", i, "] = ", kg[i]);
    writeln("costo_reducido[", i, "] = ", kg[i].reducedCost);
  }
  writeln("dual_total = ", Total.dual);
  for (var n in Nutrientes)
    writeln("dual_piso[", n, "] = ", Piso[n].dual);
  writeln("holgura_techo[grasa] = ", Techo["grasa"].slack);
}
