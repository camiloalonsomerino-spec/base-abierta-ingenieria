/*********************************************
 * Unidad 3 · Caso integrador
 * Estampa Sur: ¿comprar la segunda máquina y cuántas cajas hacer en ella?
 * Costo fijo con gran M y lote mínimo. Datos en u03_segunda_maquina.dat.
 *********************************************/

float margen = ...;   // CLP por caja extra
float fijo   = ...;   // CLP, costo fijo de la segunda máquina
int   tope   = ...;   // cajas que la máquina alcanza a hacer como máximo
int   minimo = ...;   // lote mínimo de cajas si se compra
float M      = ...;   // gran M del acoplamiento (la ajustada es el tope)

dvar int+    q;       // cajas extra que se hacen en la segunda máquina
dvar boolean y;       // 1 si se compra la segunda máquina; 0 en otro caso

dexpr float Utilidad = margen * q - fijo * y;

maximize Utilidad;

subject to {
  Tope:  q <= tope;
  Techo: q <= M * y;
  Piso:  q >= minimo * y;
}

execute {
  writeln("utilidad = ", Utilidad);
  writeln("q = ", q);
  writeln("y = ", y);
}
