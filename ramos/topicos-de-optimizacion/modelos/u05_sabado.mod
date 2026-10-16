/*********************************************
 * Unidad 5 · Caso integrador
 * Estampa Sur: el turno del sábado, en cajas de 24 prendas
 * Datos en u05_sabado.dat. Base abierta de ingeniería.
 *********************************************/

{string} Prendas  = ...;
{string} Recursos = ...;

float margen[Prendas]        = ...;   // CLP por caja de 24 prendas
float uso[Recursos][Prendas] = ...;   // minutos por caja
float disp[Recursos]         = ...;   // minutos que trae el turno

dvar int+ cajas[Prendas];             // cajas de 24 prendas que se hacen en el turno

dexpr float Margen = sum(i in Prendas) margen[i] * cajas[i];

maximize Margen;

subject to {
  forall(r in Recursos)
    Turno:
      sum(i in Prendas) uso[r][i] * cajas[i] <= disp[r];
}

execute {
  writeln("margen = ", Margen);
  for (var i in Prendas) writeln("cajas[", i, "] = ", cajas[i]);
  for (var r in Recursos) writeln("holgura[", r, "] = ", Turno[r].slack);
}
