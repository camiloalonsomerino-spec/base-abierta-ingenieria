/*********************************************
 * Unidad 3 · Ejercicio 3.6
 * Taller de impresión 3D: un modo de operación u otro (PLA o PETG) en la semana
 * Una sola binaria para todo el grupo y variables desdobladas por modo.
 * Datos en u03_e06_impresion.dat. Base abierta de ingeniería.
 *********************************************/

{string} Piezas = ...;               // soportes y carcasas
{string} Modos  = ...;               // PLA y PETG

float margen[Modos][Piezas] = ...;   // CLP por pieza según el modo
float horas[Modos][Piezas]  = ...;   // horas de impresión por pieza según el modo
float H                     = ...;   // horas de impresora en la semana
float demanda[Piezas]       = ...;   // tope de venta de cada pieza
float topeCarcasaPLA        = ...;   // en PLA solo se venden estas carcasas (interior)
float pedidoCarcasaPETG     = ...;   // en PETG hay un pedido comprometido de carcasas
float topeSoportePETG       = ...;   // en PETG el soporte se vende hasta este tope

dvar int+    x[Modos][Piezas];       // piezas de cada tipo hechas en el modo m
dvar boolean w;                      // 1 si la semana se imprime en PETG; 0 si en PLA

dexpr float Utilidad = sum(m in Modos, p in Piezas) margen[m][p] * x[m][p];

maximize Utilidad;

subject to {
  // modo PLA: rige solo si w = 0 (todo se apaga con w = 1)
  HorasPLA:   sum(p in Piezas) horas["PLA"][p] * x["PLA"][p] <= H * (1 - w);
  CarcasaPLA: x["PLA"]["carcasa"] <= topeCarcasaPLA * (1 - w);
  // modo PETG: rige solo si w = 1
  HorasPETG:  sum(p in Piezas) horas["PETG"][p] * x["PETG"][p] <= H * w;
  PedidoPETG: x["PETG"]["carcasa"] >= pedidoCarcasaPETG * w;
  SoportePETG: x["PETG"]["soporte"] <= topeSoportePETG * w;
  // la demanda vale en cualquier modo
  forall(p in Piezas)
    Demanda:
      sum(m in Modos) x[m][p] <= demanda[p];
}

execute {
  writeln("utilidad = ", Utilidad);
  writeln("w = ", w);
  for (var m in Modos)
    for (var p in Piezas)
      writeln("x[", m, "][", p, "] = ", x[m][p]);
}
