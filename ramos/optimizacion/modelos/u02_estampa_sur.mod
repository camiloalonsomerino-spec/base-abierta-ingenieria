/*********************************************
 * Unidad 2 - Caso integrador Estampa Sur, version de dos productos
 * Poleras basicas y polerones en una semana: estampado, planchado
 * y tope de venta de polerones. Datos del script del caso (DOS).
 *********************************************/

{string} Prendas = {"poleras", "polerones"};

float margen[Prendas] = [1380, 3940];   // CLP por unidad
float est[Prendas]    = [30, 90];       // segundos de estampado por unidad
float pla[Prendas]    = [20, 50];       // segundos de planchado por unidad

float capEst = 30 * 3600;               // 30 h de estampado en segundos
float capPla = 18 * 3600;               // 18 h de planchado en segundos
float demPolerones = 830;               // polerones que se pueden vender

dvar float+ x[Prendas];

maximize sum(i in Prendas) margen[i] * x[i];

subject to {
  ctEstampado: sum(i in Prendas) est[i] * x[i] <= capEst;
  ctPlanchado: sum(i in Prendas) pla[i] * x[i] <= capPla;
  ctDemanda:   x["polerones"] <= demPolerones;
}

execute {
  writeln("z = ", cplex.getObjValue());
  for (var i in Prendas) writeln("x_" + i + " = ", x[i]);
  writeln("holgura_estampado = ", ctEstampado.slack);
  writeln("holgura_planchado = ", ctPlanchado.slack);
  writeln("holgura_demanda = ", ctDemanda.slack);
  writeln("dual_estampado = ", ctEstampado.dual);
  writeln("dual_planchado = ", ctPlanchado.dual);
}
