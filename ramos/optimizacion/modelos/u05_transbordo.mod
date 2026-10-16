/*********************************************
 * Unidad 5 · Modelamiento lineal II (ejercicio 5.6)
 * Transbordo: plantas → centros de distribución → clientes.
 * En cada centro lo que sale tiene que haber llegado (balance = 0).
 * Datos en u05_transbordo.dat. Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS
{string} Plantas  = ...;
{string} Centros  = ...;
{string} Clientes = ...;

// PARÁMETROS
float oferta[Plantas]             = ...;   // toneladas por mes
float capCentro[Centros]          = ...;   // toneladas que puede recibir cada centro
float demanda[Clientes]           = ...;   // toneladas por mes
float cPC[Plantas][Centros]       = ...;   // CLP por tonelada, primer tramo
float cCK[Centros][Clientes]      = ...;   // CLP por tonelada, segundo tramo

// VARIABLES DE DECISIÓN
dvar float+ x[Plantas][Centros];
dvar float+ y[Centros][Clientes];

// OBJETIVO
minimize sum(p in Plantas, c in Centros) cPC[p][c] * x[p][c]
       + sum(c in Centros, k in Clientes) cCK[c][k] * y[c][k];

// RESTRICCIONES
subject to {
  forall(p in Plantas)
    Oferta: sum(c in Centros) x[p][c] <= oferta[p];
  forall(c in Centros) {
    Balance:   sum(p in Plantas) x[p][c] - sum(k in Clientes) y[c][k] == 0;
    CapCentro: sum(p in Plantas) x[p][c] <= capCentro[c];
  }
  forall(k in Clientes)
    Demanda: sum(c in Centros) y[c][k] >= demanda[k];
}

// SALIDA
execute {
  writeln("costo = ", cplex.getObjValue());
  for (var p in Plantas) for (var c in Centros) writeln("x[", p, "][", c, "] = ", x[p][c]);
  for (var c in Centros) for (var k in Clientes) writeln("y[", c, "][", k, "] = ", y[c][k]);
  for (var p in Plantas)  writeln("dual_oferta[", p, "] = ", Oferta[p].dual);
  for (var c in Centros)  writeln("dual_balance[", c, "] = ", Balance[c].dual);
  for (var c in Centros)  writeln("dual_capCentro[", c, "] = ", CapCentro[c].dual);
  for (var k in Clientes) writeln("dual_demanda[", k, "] = ", Demanda[k].dual);
}
