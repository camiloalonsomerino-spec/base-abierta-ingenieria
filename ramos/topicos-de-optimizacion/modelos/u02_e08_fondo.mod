// Ejercicio 2.8 · fondo concursable: mochila con dos recursos y reglas
int n = ...;
range Iniciativas = 1..n;
{int} Rurales = ...;
float inversion[Iniciativas] = ...;   // millones de CLP
float horas[Iniciativas]     = ...;   // horas de equipo técnico
float puntos[Iniciativas]    = ...;   // puntaje de impacto
float presupuesto            = ...;
float horasDisp              = ...;

dvar boolean x[Iniciativas];          // 1 si se financia la iniciativa j, 0 en otro caso

maximize sum(j in Iniciativas) puntos[j] * x[j];

subject to {
  Presupuesto: sum(j in Iniciativas) inversion[j] * x[j] <= presupuesto;
  Horas:       sum(j in Iniciativas) horas[j] * x[j] <= horasDisp;
  Rurales2:    sum(j in Rurales) x[j] >= 2;
  Juntas:      x[4] == x[5];
}

execute {
  for (var j in Iniciativas) writeln("x[", j, "] = ", x[j]);
}
