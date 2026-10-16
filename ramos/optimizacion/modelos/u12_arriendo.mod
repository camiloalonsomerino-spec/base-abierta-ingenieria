/*********************************************
 * Unidad 12 · ejercicio 12.10
 * Amasandería: cuántas horas de horno y de amasado arrendar.
 * Más allá del rango de un lado derecho el precio sombra cambia, así que
 * la compra de recursos se decide dentro del modelo y no con el precio.
 * Datos en el mismo archivo (modelo pequeño).
 *********************************************/

{string} Panes = {"hallulla", "marraqueta"};
float margen[Panes]   = [5000, 4000];       // CLP por lote
float horno[Panes]    = [2, 1];             // horas de horno por lote
float amasado[Panes]  = [1, 3];             // horas de amasado por lote
float horasHorno      = 40;
float horasAmasado    = 45;
float topeHallulla    = 18;
float precioHorno     = 1500;               // CLP por hora arrendada
float precioAmasado   = 650;
float maxHorno        = 10;                 // horas que se pueden arrendar
float maxAmasado      = 30;

dvar float+ x[Panes];
dvar float+ h;                              // horas de horno arrendadas
dvar float+ a;                              // horas de amasado arrendadas

dexpr float MargenNeto = sum(p in Panes) margen[p] * x[p] - precioHorno * h - precioAmasado * a;

maximize MargenNeto;

subject to {
  Horno:    sum(p in Panes) horno[p] * x[p]   <= horasHorno + h;
  Amasado:  sum(p in Panes) amasado[p] * x[p] <= horasAmasado + a;
  Tope:     x["hallulla"] <= topeHallulla;
  LimH:     h <= maxHorno;
  LimA:     a <= maxAmasado;
}

execute {
  writeln("margen_neto = ", MargenNeto);
  for (var p in Panes) writeln("x[", p, "] = ", x[p]);
  writeln("horas_horno = ", h);
  writeln("horas_amasado = ", a);
}
