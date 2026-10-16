/*********************************************
 * Unidad 4 · Ejercicio 4.5 (pauta) · ensamblaje de un vino
 * Un solo producto: 9.600 L mezclando tres vinos base al menor costo.
 * Datos en u04_e05_ensamblaje.dat. Base abierta de ingeniería.
 *********************************************/

{string} Vinos = ...;
string principal = ...;              // la cepa que debe ser al menos la mitad

float alcohol[Vinos] = ...;          // % de alcohol
float costo[Vinos]   = ...;          // CLP por litro
float disp[Vinos]    = ...;          // litros disponibles
float total   = ...;                 // litros del ensamblaje
float alc_min = ...;
float alc_max = ...;
float part_min = ...;                // fracción mínima de la cepa principal

dvar float+ x[Vinos];                // litros de cada vino base

dexpr float litros = sum(v in Vinos) x[v];

minimize sum(v in Vinos) costo[v] * x[v];

subject to {
  Total:    litros == total;
  AlcMax:   sum(v in Vinos) alcohol[v] * x[v] <= alc_max * litros;
  AlcMin:   sum(v in Vinos) alcohol[v] * x[v] >= alc_min * litros;
  Cepa:     x[principal] >= part_min * litros;
  forall(v in Vinos)
    Disp:   x[v] <= disp[v];
}

execute {
  writeln("costo = ", cplex.getObjValue());
  for (var v in Vinos)
    writeln("x_", v, " = ", x[v]);
  writeln("dual_total = ", Total.dual);
}
