/*********************************************
 * Unidad 5 · Modelamiento lineal II (ejemplo resuelto)
 * Pellet del Laja: producción de cuatro meses con turno regular,
 * turno extra e inventario en bodega. Datos en u05_pellets.dat.
 * Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS
int NMeses = ...;
range Meses = 1..NMeses;

// PARÁMETROS
float demanda[Meses] = ...;   // bolsas por mes
float capReg = ...;           // bolsas por mes en turno regular
float cReg   = ...;           // CLP por bolsa en turno regular
float capExt = ...;           // bolsas por mes en turno extra
float cExt   = ...;           // CLP por bolsa en turno extra
float cInv   = ...;           // CLP por bolsa guardada al cierre de un mes
float bodega = ...;           // bolsas que caben en la bodega
float inv0   = ...;           // bolsas al empezar abril
float invFin = ...;           // bolsas que deben quedar al cierre de julio

// VARIABLES DE DECISIÓN
dvar float+ R[Meses];         // bolsas en turno regular
dvar float+ E[Meses];         // bolsas en turno extra
dvar float+ I[Meses];         // bolsas en bodega al cierre del mes

// OBJETIVO
minimize sum(t in Meses) (cReg * R[t] + cExt * E[t] + cInv * I[t]);

// RESTRICCIONES
subject to {
  forall(t in Meses) {
    Regular: R[t] <= capReg;
    Extra:   E[t] <= capExt;
    Bodega:  I[t] <= bodega;
  }
  // balance: lo que había + lo que se produce − lo que queda = lo que se vende
  forall(t in Meses: t == 1)
    Balance1: inv0 + R[t] + E[t] - I[t] == demanda[t];
  forall(t in Meses: t > 1)
    Balance: I[t-1] + R[t] + E[t] - I[t] == demanda[t];
  Final: I[NMeses] >= invFin;
}

// SALIDA
execute {
  writeln("costo = ", cplex.getObjValue());
  for (var t in Meses) {
    writeln("R[", t, "] = ", R[t]);
    writeln("E[", t, "] = ", E[t]);
    writeln("I[", t, "] = ", I[t]);
  }
  writeln("dual_balance[1] = ", Balance1[1].dual);
  for (var t = 2; t <= NMeses; t++)
    writeln("dual_balance[", t, "] = ", Balance[t].dual);
  writeln("dual_final = ", Final.dual);
}
