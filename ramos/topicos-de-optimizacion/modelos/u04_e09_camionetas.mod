/*********************************************
 * Unidad 4 · Ejercicio 4.9
 * Ruteo de vehículos con capacidad (CVRP): K camionetas salen y vuelven al
 * taller. La carga acumulada u hace de MTZ: elimina subtours y respeta la
 * capacidad a la vez. Datos en u04_e09_camionetas.dat.
 *********************************************/

{string} Lugares = ...;
string   base    = ...;
float    d[Lugares][Lugares] = ...;   // km de ruta más corta
float    q[Lugares]          = ...;   // cajas que pide cada tienda (la base pide 0)
float    Q                   = ...;   // cajas por camioneta
int      K                   = ...;   // camionetas disponibles

dvar boolean x[Lugares][Lugares];     // 1 si una camioneta va de i directo a j; 0 en otro caso
dvar float+  u[Lugares];              // cajas entregadas por esa camioneta hasta j, inclusive

dexpr float Km = sum(i in Lugares, j in Lugares: i != j) d[i][j] * x[i][j];

minimize Km;

subject to {
  forall(i in Lugares)
    SinLazo:
      x[i][i] == 0;
  forall(i in Lugares: i != base)
    Sale:
      sum(j in Lugares: j != i) x[i][j] == 1;
  forall(j in Lugares: j != base)
    Entra:
      sum(i in Lugares: i != j) x[i][j] == 1;
  SalenDelTaller:
    sum(j in Lugares: j != base) x[base][j] <= K;
  VuelvenAlTaller:
    sum(i in Lugares: i != base) x[i][base] == sum(j in Lugares: j != base) x[base][j];
  // carga acumulada: si se va de i a j (j no es la base), en j se lleva al menos q[j] más
  forall(i in Lugares, j in Lugares: j != base && i != j)
    Carga:
      u[j] >= u[i] + q[j] - Q * (1 - x[i][j]);
  CargaBase:
    u[base] == 0;
  forall(i in Lugares: i != base)
    Rango:
      q[i] <= u[i] <= Q;
}

execute {
  writeln("km = ", Km);
  var k = 0;
  for (var j in Lugares)
    if (j != base) k = k + x[base][j];
  writeln("camionetas = ", k);
}
