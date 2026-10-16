/*********************************************
 * Unidad 6 · caso integrador Estampa Sur
 * Programación por metas: margen de al menos metaMargen y tinta de a lo más
 * metaTinta, con la tinta de la semana como tope duro. Se minimizan las
 * desviaciones no deseadas en términos relativos, con pesos wMargen y 1 − wMargen.
 * Datos en u06_estampa_metas.dat (cifras del script del caso).
 * Base abierta de ingeniería.
 *********************************************/

{string} Prendas = ...;
float margen[Prendas]  = ...;
float est[Prendas]     = ...;
float pla[Prendas]     = ...;
float tinta[Prendas]   = ...;
float demanda[Prendas] = ...;
float capEst = ...;
float capPla = ...;
float capTinta   = ...;          // gramos de tinta de la semana (tope duro)
float metaMargen = ...;
float metaTinta  = ...;
float wMargen    = ...;

dvar float+ x[Prendas];
dvar float+ dmMenos;  dvar float+ dmMas;    // margen bajo / sobre la meta
dvar float+ dtMenos;  dvar float+ dtMas;    // tinta bajo / sobre la meta

dexpr float Margen = sum(p in Prendas) margen[p] * x[p];
dexpr float Tinta  = sum(p in Prendas) tinta[p] * x[p];

minimize wMargen * dmMenos / metaMargen + (1 - wMargen) * dtMas / metaTinta;

subject to {
  Estampado: sum(p in Prendas) est[p] * x[p] <= capEst;
  Planchado: sum(p in Prendas) pla[p] * x[p] <= capPla;
  TintaDura: Tinta <= capTinta;
  forall(p in Prendas) Demanda: x[p] <= demanda[p];
  MetaMargen: Margen + dmMenos - dmMas == metaMargen;
  MetaTinta:  Tinta  + dtMenos - dtMas == metaTinta;
}

execute {
  writeln("margen = ", Margen);
  writeln("tinta = ", Tinta);
  writeln("falta_margen = ", dmMenos);
  writeln("exceso_tinta = ", dtMas);
  for (var p in Prendas) writeln("x[", p, "] = ", x[p]);
}
