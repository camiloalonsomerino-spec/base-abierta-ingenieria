/*********************************************
 * Unidad 10 · Asignación
 * Personas a tareas al menor costo, con topes por persona, tareas optativas y pares prohibidos.
 * Datos en u10_*.dat. Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS
{string} Personas = ...;
{string} Tareas   = ...;
tuple Par { string p; string t; }
{Par} Prohibidos = ...;                 // pares que no se pueden asignar (puede ir vacío)

// PARÁMETROS
float costo[Personas][Tareas] = ...;    // minutos o pesos de que p haga t
int   minTareas[Personas]     = ...;    // tareas que p debe tomar como mínimo
int   maxTareas[Personas]     = ...;    // tareas que p puede tomar como máximo
int   obligatoria[Tareas]     = ...;    // 1 si t se tiene que hacer; 0 si puede quedar sin hacer

// VARIABLES DE DECISIÓN
dvar boolean x[Personas][Tareas];       // 1 si la persona p hace la tarea t; 0 en otro caso

// OBJETIVO
minimize sum(p in Personas, t in Tareas) costo[p][t] * x[p][t];

// RESTRICCIONES
subject to {
  forall(p in Personas) {
    Minimo:  sum(t in Tareas) x[p][t] >= minTareas[p];
    Maximo:  sum(t in Tareas) x[p][t] <= maxTareas[p];
  }
  forall(t in Tareas) {
    UnaVez:  sum(p in Personas) x[p][t] <= 1;
    Cubrir:  sum(p in Personas) x[p][t] >= obligatoria[t];
  }
  forall(<p, t> in Prohibidos)
    Prohibido: x[p][t] == 0;
}

// SALIDA
execute {
  writeln("total = ", cplex.getObjValue());
  for (var p in Personas) for (var t in Tareas) if (x[p][t] == 1) writeln("x[", p, "][", t, "] = 1");
}
