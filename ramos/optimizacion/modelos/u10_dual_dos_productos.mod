/*********************************************
 * Unidad 10 · Caso integrador · el dual de la versión de dos productos
 * y1: CLP por segundo de estampado · y2: CLP por segundo de planchado ·
 * y3: CLP por polerón de demanda. Cada prenda tiene que valer, en recursos,
 * al menos su margen. El óptimo tiene que igualar el margen del primal.
 *********************************************/
{string} Prendas = {"poleras", "polerones"};
float margen[Prendas] = [1380, 3940];
float est[Prendas]    = [30, 90];
float pla[Prendas]    = [20, 50];
float capEst = 30 * 3600;
float capPla = 18 * 3600;
float demPolerones = 830;

dvar float+ y1;
dvar float+ y2;
dvar float+ y3;

minimize capEst * y1 + capPla * y2 + demPolerones * y3;

subject to {
  ctPoleras:   est["poleras"] * y1 + pla["poleras"] * y2 >= margen["poleras"];
  ctPolerones: est["polerones"] * y1 + pla["polerones"] * y2 + y3 >= margen["polerones"];
}

execute {
  writeln("y_estampado = ", y1);
  writeln("y_planchado = ", y2);
  writeln("y_demanda = ", y3);
  writeln("x_poleras = ", ctPoleras.dual);
  writeln("x_polerones = ", ctPolerones.dual);
}
