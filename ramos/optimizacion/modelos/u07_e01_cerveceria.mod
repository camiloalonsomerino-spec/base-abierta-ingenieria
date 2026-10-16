/*********************************************
 * Unidad 7 · Ejercicio 7.1 (pauta)
 * Cervecería artesanal: barriles de lager y stout al mes
 * Modelo escrito «a mano», sin .dat (como el primer taller).
 *********************************************/

dvar float+ L;      // barriles de lager al mes
dvar float+ S;      // barriles de stout al mes

dexpr float Maceracion   = 3*L + 5*S;     // horas de maceración usadas
dexpr float Fermentacion = 2*L + 2*S;     // tanques-semana usados

maximize 23000*L + 29000*S;

subject to {
  Rt_maceracion:   Maceracion   <= 150;
  Rt_fermentacion: Fermentacion <= 80;
}

execute {
  writeln("margen = ", cplex.getObjValue());
  writeln("L = ", L);
  writeln("S = ", S);
  writeln("maceracion_usada = ", Maceracion);
  writeln("dual_maceracion = ", Rt_maceracion.dual);
  writeln("dual_fermentacion = ", Rt_fermentacion.dual);
}
