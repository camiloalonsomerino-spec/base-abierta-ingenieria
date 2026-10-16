/*********************************************
 * Unidad 3 · Ejercicio 3.9
 * Kombucha artesanal: costo fijo y lote mínimo por sabor, un turno de
 * embotellado entre tres (función con N valores) y a lo más dos sabores.
 * Datos en u03_e09_kombucha.dat. Base abierta de ingeniería.
 *********************************************/

{string} Sabores = ...;
{string} Turnos  = ...;

float margen[Sabores]  = ...;   // CLP por litro
float fijo[Sabores]    = ...;   // CLP por semana si se fermenta el sabor
float minimo[Sabores]  = ...;   // litros, lote mínimo del sabor
float demanda[Sabores] = ...;   // litros que se venden como máximo
float cap[Turnos]      = ...;   // litros que embotella cada turno en la semana
float costo[Turnos]    = ...;   // CLP, costo fijo semanal del turno
int   maxSabores       = ...;   // sabores distintos por semana

// gran M ajustada de cada sabor: su demanda (nunca pasa del turno más grande)
float M[s in Sabores] = minl(demanda[s], max(k in Turnos) cap[k]);

dvar float+  x[Sabores];        // litros de cada sabor en la semana
dvar boolean y[Sabores];        // 1 si se fermenta el sabor s; 0 en otro caso
dvar boolean t[Turnos];         // 1 si se contrata el turno k; 0 en otro caso

dexpr float Capacidad = sum(k in Turnos) cap[k] * t[k];
dexpr float Utilidad  = sum(s in Sabores) (margen[s] * x[s] - fijo[s] * y[s])
                      - sum(k in Turnos) costo[k] * t[k];

maximize Utilidad;

subject to {
  UnTurno:
    sum(k in Turnos) t[k] == 1;
  Embotellado:
    sum(s in Sabores) x[s] <= Capacidad;
  forall(s in Sabores)
    Techo:
      x[s] <= M[s] * y[s];
  forall(s in Sabores)
    Piso:
      x[s] >= minimo[s] * y[s];
  ASumo:
    sum(s in Sabores) y[s] <= maxSabores;
}

execute {
  writeln("utilidad = ", Utilidad);
  writeln("capacidad = ", Capacidad);
  for (var s in Sabores) {
    writeln("x[", s, "] = ", x[s]);
    writeln("y[", s, "] = ", y[s]);
  }
  for (var k in Turnos)
    writeln("t[", k, "] = ", t[k]);
}
