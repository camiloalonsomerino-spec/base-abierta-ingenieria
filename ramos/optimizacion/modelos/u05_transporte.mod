/*********************************************
 * Unidad 5 · Modelamiento lineal II
 * Problema de transporte genérico: orígenes con oferta máxima, destinos con
 * demanda mínima y un costo por unidad en cada ruta. El mismo modelo sirve
 * para todos los .dat de la unidad (huevos, leche, buses, tiendas...):
 * la asignación es un transporte con ofertas y demandas iguales a 1.
 * Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS
{string} Origenes = ...;
{string} Destinos = ...;

// PARÁMETROS
float oferta[Origenes]            = ...;   // unidades que puede despachar cada origen
float demanda[Destinos]           = ...;   // unidades que pide cada destino
float costo[Origenes][Destinos]   = ...;   // CLP (o minutos) por unidad en la ruta

// VARIABLES DE DECISIÓN
dvar float+ x[Origenes][Destinos];         // unidades enviadas de o a d

// OBJETIVO
minimize sum(o in Origenes, d in Destinos) costo[o][d] * x[o][d];

// RESTRICCIONES
subject to {
  forall(o in Origenes)
    Oferta: sum(d in Destinos) x[o][d] <= oferta[o];     // se suma sobre los DESTINOS
  forall(d in Destinos)
    Demanda: sum(o in Origenes) x[o][d] >= demanda[d];   // se suma sobre los ORÍGENES
}

// SALIDA
execute {
  writeln("costo = ", cplex.getObjValue());
  for (var o in Origenes)
    for (var d in Destinos)
      writeln("x[", o, "][", d, "] = ", x[o][d]);
  for (var o in Origenes)
    writeln("dual_oferta[", o, "] = ", Oferta[o].dual);
  for (var d in Destinos)
    writeln("dual_demanda[", d, "] = ", Demanda[d].dual);
}
