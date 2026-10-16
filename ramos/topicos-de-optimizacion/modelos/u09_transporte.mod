/*********************************************
 * Unidad 9 · Problema de transporte
 * Envíos de orígenes a destinos al menor costo (oferta <=, demanda >=).
 * Datos en u09_*.dat. Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS
{string} Orig = ...;                     // talleres, plantas o bodegas
{string} Dest = ...;                     // tiendas o clientes
tuple Ruta { string o; string d; }
{Ruta} Prohibidas = ...;                 // rutas que no se pueden usar (puede ir vacío)

// PARÁMETROS
int   oferta[Orig]       = ...;          // unidades disponibles por semana
int   demanda[Dest]      = ...;          // unidades pedidas por semana
float costo[Orig][Dest]  = ...;          // CLP por unidad enviada

// VARIABLES DE DECISIÓN
dvar float+ x[Orig][Dest];               // unidades enviadas de o a d (0 si la ruta no se usa)

// OBJETIVO
minimize sum(o in Orig, d in Dest) costo[o][d] * x[o][d];

// RESTRICCIONES
subject to {
  forall(o in Orig)
    Oferta:    sum(d in Dest) x[o][d] <= oferta[o];
  forall(d in Dest)
    Demanda:   sum(o in Orig) x[o][d] >= demanda[d];
  forall(<o, d> in Prohibidas)
    Prohibida: x[o][d] == 0;
}

// SALIDA
execute {
  writeln("costo = ", cplex.getObjValue());
  for (var o in Orig) for (var d in Dest) if (x[o][d] > 0) writeln("x[", o, "][", d, "] = ", x[o][d]);
  for (var o in Orig) writeln("dual_oferta[", o, "] = ", Oferta[o].dual);
  for (var d in Dest) writeln("dual_demanda[", d, "] = ", Demanda[d].dual);
  for (var o in Orig) for (var d in Dest) if (x[o][d] == 0) writeln("cr[", o, "][", d, "] = ", x[o][d].reducedCost);
}
