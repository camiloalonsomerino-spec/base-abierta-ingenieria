// Unidad 2 · ejemplo: seis proyectos de una cooperativa de agua potable rural
int n = ...;
range Proyectos = 1..n;
float inversion[Proyectos] = ...;   // millones de CLP
float van[Proyectos]       = ...;   // millones de CLP
float presupuesto          = ...;   // millones de CLP
int   maxProyectos         = ...;

dvar boolean x[Proyectos];          // 1 si se ejecuta el proyecto j, 0 en otro caso

maximize sum(j in Proyectos) van[j] * x[j];

subject to {
  Presupuesto:   sum(j in Proyectos) inversion[j] * x[j] <= presupuesto;
  R1_telemetria: x[6] <= x[3];                 // la telemetría exige los medidores
  R2_red:        x[4] <= x[1];                 // la red al sector alto exige el estanque
  R3_terreno:    x[2] + x[5] <= 1;             // bomba solar y cloración: no ambas
  R4_sanitaria:  x[3] + x[5] >= 1;             // al menos medidores o cloración
  R5_gestion:    sum(j in Proyectos) x[j] <= maxProyectos;
}

execute {
  for (var j in Proyectos) writeln("x[", j, "] = ", x[j]);
}
