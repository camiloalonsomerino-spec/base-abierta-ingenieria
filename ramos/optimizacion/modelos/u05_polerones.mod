/*********************************************
 * Unidad 5 · caso integrador Estampa Sur
 * Polerones en cuatro semanas: producción con tope semanal, inventario con
 * tope de bodega y costo por unidad guardada. Datos en u05_polerones.dat
 * (las cifras del script del caso). Base abierta de ingeniería.
 *********************************************/

int NSemanas = ...;
range Semanas = 1..NSemanas;
float demanda[Semanas] = ...;     // polerones por semana
float cap    = ...;               // polerones que caben en una semana de taller
float invMax = ...;               // polerones que caben guardados
float cInv   = ...;               // CLP por polerón y semana guardado

dvar float+ x[Semanas];           // polerones producidos
dvar float+ I[Semanas];           // polerones guardados al cierre (no hay inventario inicial)

minimize sum(t in Semanas) cInv * I[t];

subject to {
  forall(t in Semanas) {
    Capacidad: x[t] <= cap;
    Bodega:    I[t] <= invMax;
    Balance:   (t > 1 ? I[t-1] : 0) + x[t] - I[t] == demanda[t];
  }
}

execute {
  writeln("costo = ", cplex.getObjValue());
  for (var t in Semanas) {
    writeln("x[", t, "] = ", x[t]);
    writeln("I[", t, "] = ", I[t]);
    writeln("dual_capacidad[", t, "] = ", Capacidad[t].dual);
    writeln("dual_balance[", t, "] = ", Balance[t].dual);
  }
}
