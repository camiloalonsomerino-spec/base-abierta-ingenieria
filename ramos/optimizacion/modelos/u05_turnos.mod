/*********************************************
 * Unidad 5 · Modelamiento lineal II (ejercicio 5.7)
 * Personal por turnos: cada persona trabaja 8 horas seguidas (dos bloques
 * de 4 horas) y el día es cíclico (el turno de las 20:00 sigue a las 0:00).
 * Datos en u05_turnos.dat. Base abierta de ingeniería.
 *********************************************/

int NBloques = ...;
range Bloques = 1..NBloques;
int req[Bloques] = ...;              // personas necesarias en cada bloque

dvar int+ x[Bloques];                // personas que ENTRAN al inicio del bloque b

minimize sum(b in Bloques) x[b];

subject to {
  // el bloque b lo cubren los que entran en b y los que entraron en el bloque anterior
  forall(b in Bloques: b == 1)
    Cubre1: x[b] + x[NBloques] >= req[b];
  forall(b in Bloques: b > 1)
    Cubre: x[b] + x[b-1] >= req[b];
}

execute {
  writeln("personas = ", cplex.getObjValue());
  for (var b in Bloques) writeln("x[", b, "] = ", x[b]);
}
