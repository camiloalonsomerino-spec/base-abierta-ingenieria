/*********************************************
 * Unidad 9 · Caso integrador · Estampa Sur con un compromiso mínimo
 * Versión de dos productos de la unidad 2 (30 h de estampado, 18 h de planchado,
 * demanda máxima de 830 polerones) más un pedido firmado de al menos 780 polerones.
 *********************************************/
{string} Prendas = {"poleras", "polerones"};
float margen[Prendas] = [1380, 3940];      // CLP por unidad
float est[Prendas]    = [30, 90];          // segundos de estampado por unidad
float pla[Prendas]    = [20, 50];          // segundos de planchado por unidad
float capEst = 30 * 3600;                  // segundos de estampado en la semana
float capPla = 18 * 3600;                  // segundos de planchado en la semana
float demPolerones = 830;                  // demanda máxima de polerones
float compromiso = 780;                    // polerones ya comprometidos

dvar float+ x[Prendas];

maximize sum(p in Prendas) margen[p] * x[p];

subject to {
  ctEstampado:  sum(p in Prendas) est[p] * x[p] <= capEst;
  ctPlanchado:  sum(p in Prendas) pla[p] * x[p] <= capPla;
  ctDemanda:    x["polerones"] <= demPolerones;
  ctCompromiso: x["polerones"] >= compromiso;
}

execute {
  writeln("x_poleras = ", x["poleras"]);
  writeln("x_polerones = ", x["polerones"]);
  writeln("dual_estampado = ", ctEstampado.dual);
  writeln("dual_planchado = ", ctPlanchado.dual);
  writeln("dual_demanda = ", ctDemanda.dual);
  writeln("dual_compromiso = ", ctCompromiso.dual);
}
