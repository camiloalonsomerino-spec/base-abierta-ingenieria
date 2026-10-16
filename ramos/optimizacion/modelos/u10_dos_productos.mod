/*********************************************
 * Unidad 10 · Caso integrador · Estampa Sur, versión de dos productos (el primal)
 * La misma de las unidades 2 y 8: 30 h de estampado, 18 h de planchado y a lo más
 * 830 polerones. El .dual de cada restricción es el precio de ese recurso.
 *********************************************/
{string} Prendas = {"poleras", "polerones"};
float margen[Prendas] = [1380, 3940];      // CLP por unidad
float est[Prendas]    = [30, 90];          // segundos de estampado por unidad
float pla[Prendas]    = [20, 50];          // segundos de planchado por unidad
float capEst = 30 * 3600;
float capPla = 18 * 3600;
float demPolerones = 830;

dvar float+ x[Prendas];

maximize sum(p in Prendas) margen[p] * x[p];

subject to {
  ctEstampado: sum(p in Prendas) est[p] * x[p] <= capEst;
  ctPlanchado: sum(p in Prendas) pla[p] * x[p] <= capPla;
  ctDemanda:   x["polerones"] <= demPolerones;
}

execute {
  writeln("x_poleras = ", x["poleras"]);
  writeln("x_polerones = ", x["polerones"]);
  writeln("y_estampado = ", ctEstampado.dual);
  writeln("y_planchado = ", ctPlanchado.dual);
  writeln("y_demanda = ", ctDemanda.dual);
}
