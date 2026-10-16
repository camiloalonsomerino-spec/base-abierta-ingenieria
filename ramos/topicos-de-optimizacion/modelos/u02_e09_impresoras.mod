// Ejercicio 2.9 · ocho piezas en tres impresoras 3D: terminar todo lo antes posible
int nPiezas     = ...;
int nImpresoras = ...;
range Piezas     = 1..nPiezas;
range Impresoras = 1..nImpresoras;
float horas[Piezas] = ...;            // horas de impresión de cada pieza
int juntaA = ...;      int juntaB = ...;       // van en la misma impresora
int separadaA = ...;   int separadaB = ...;    // van en impresoras distintas

dvar boolean x[Piezas][Impresoras];   // 1 si la pieza j se imprime en la impresora k, 0 en otro caso
dvar float+  Cmax;                    // horas hasta que termina la impresora más cargada

minimize Cmax;

subject to {
  forall(j in Piezas)
    Una:       sum(k in Impresoras) x[j][k] == 1;
  forall(k in Impresoras)
    Carga:     sum(j in Piezas) horas[j] * x[j][k] <= Cmax;
  forall(k in Impresoras)
    Juntas:    x[juntaA][k] == x[juntaB][k];
  forall(k in Impresoras)
    Separadas: x[separadaA][k] + x[separadaB][k] <= 1;
}

execute {
  writeln("cmax = ", Cmax);
}
