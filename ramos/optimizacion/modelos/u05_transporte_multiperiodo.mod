/*********************************************
 * Unidad 5 · Modelamiento lineal II (ejercicio 5.9)
 * Transporte multiperíodo: cada planta produce, guarda inventario y despacha
 * a los clientes mes a mes. Datos en u05_transporte_multiperiodo.dat.
 * Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS
int NMeses = ...;
range Meses = 1..NMeses;
{string} Plantas  = ...;
{string} Clientes = ...;

// PARÁMETROS
float cap[Plantas]               = ...;   // unidades por mes
float cProd[Plantas]             = ...;   // CLP por unidad producida
float cInv[Plantas]              = ...;   // CLP por unidad guardada al cierre de mes
float cEnv[Plantas][Clientes]    = ...;   // CLP por unidad enviada
float dem[Clientes][Meses]       = ...;   // unidades pedidas

// VARIABLES DE DECISIÓN
dvar float+ Y[Plantas][Meses];             // producción
dvar float+ Z[Plantas][Meses];             // inventario al cierre del mes
dvar float+ X[Plantas][Clientes][Meses];   // envíos

// OBJETIVO
minimize sum(p in Plantas, t in Meses) (cProd[p] * Y[p][t] + cInv[p] * Z[p][t])
       + sum(p in Plantas, k in Clientes, t in Meses) cEnv[p][k] * X[p][k][t];

// RESTRICCIONES
subject to {
  forall(p in Plantas, t in Meses)
    Capacidad: Y[p][t] <= cap[p];
  // lo producido + lo guardado del mes anterior − lo que queda = lo que se despacha
  forall(p in Plantas, t in Meses)
    Balance: Y[p][t] + (t > 1 ? Z[p][t-1] : 0) - Z[p][t] == sum(k in Clientes) X[p][k][t];
  forall(k in Clientes, t in Meses)
    Demanda: sum(p in Plantas) X[p][k][t] >= dem[k][t];
}

// SALIDA
execute {
  writeln("costo = ", cplex.getObjValue());
  for (var p in Plantas) for (var t in Meses) {
    writeln("Y[", p, "][", t, "] = ", Y[p][t]);
    writeln("Z[", p, "][", t, "] = ", Z[p][t]);
    for (var k in Clientes) writeln("X[", p, "][", k, "][", t, "] = ", X[p][k][t]);
  }
  for (var k in Clientes) for (var t in Meses)
    writeln("dual_demanda[", k, "][", t, "] = ", Demanda[k][t].dual);
}
