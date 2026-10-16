/*********************************************
 * Unidad 3 · Ejemplo resuelto
 * Taller de velas: costo fijo de moldes, gran M ajustada y lote mínimo
 * Datos en u03_velas.dat. Base abierta de ingeniería.
 *********************************************/

{string} Velas    = ...;
{string} Recursos = ...;

float margen[Velas]        = ...;   // CLP por vela
float fijo[Velas]          = ...;   // CLP por semana si se prepara la línea
float uso[Recursos][Velas] = ...;   // kg de cera o minutos de vertido por vela
float disp[Recursos]       = ...;   // kg o minutos por semana
float demanda[Velas]       = ...;   // velas que se venden como máximo
float minimo[Velas]        = ...;   // lote mínimo si se prepara la línea

// gran M ajustada: lo máximo que cabe de cada vela, mirando demanda y recursos
float M[v in Velas] = minl(demanda[v], min(r in Recursos) disp[r] / uso[r][v]);

dvar int+    x[Velas];              // velas de cada línea en la semana
dvar boolean y[Velas];              // 1 si se prepara la línea v; 0 en otro caso

dexpr float Utilidad = sum(v in Velas) (margen[v] * x[v] - fijo[v] * y[v]);

maximize Utilidad;

subject to {
  forall(r in Recursos)
    Recurso:
      sum(v in Velas) uso[r][v] * x[v] <= disp[r];
  forall(v in Velas)
    Demanda:
      x[v] <= demanda[v];
  forall(v in Velas)
    Techo:
      x[v] <= M[v] * y[v];
  forall(v in Velas)
    Piso:
      x[v] >= minimo[v] * y[v];
}

execute {
  writeln("utilidad = ", Utilidad);
  for (var v in Velas) {
    writeln("M[", v, "] = ", M[v]);
    writeln("x[", v, "] = ", x[v]);
    writeln("y[", v, "] = ", y[v]);
  }
}
