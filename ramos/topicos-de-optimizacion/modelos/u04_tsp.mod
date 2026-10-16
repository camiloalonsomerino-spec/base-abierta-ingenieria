/*********************************************
 * Unidad 4 · Vendedor viajero con eliminación de subtours MTZ
 * Un modelo para dos juegos de datos: u04_ascensores.dat (ejemplo resuelto)
 * y u04_ruta_camion.dat (caso integrador). Base abierta de ingeniería.
 *********************************************/

{string} Lugares = ...;              // la base y los lugares que hay que visitar
string   base    = ...;              // desde donde sale y adonde vuelve la ruta
float    d[Lugares][Lugares] = ...;  // km entre cada par de lugares

int n = card(Lugares);

dvar boolean x[Lugares][Lugares];    // 1 si la ruta va de i directo a j; 0 en otro caso
dvar float+  u[Lugares];             // posición del lugar en la ruta (la base es la 1)

dexpr float Km = sum(i in Lugares, j in Lugares: i != j) d[i][j] * x[i][j];

minimize Km;

subject to {
  forall(i in Lugares)
    SinLazo:
      x[i][i] == 0;
  forall(i in Lugares)
    Sale:
      sum(j in Lugares: j != i) x[i][j] == 1;
  forall(j in Lugares)
    Entra:
      sum(i in Lugares: i != j) x[i][j] == 1;
  // MTZ: si la ruta va de i a j (ninguno es la base), j queda al menos una posición después de i
  forall(i in Lugares, j in Lugares: i != base && j != base && i != j)
    MTZ:
      u[i] - u[j] + 1 <= (n - 1) * (1 - x[i][j]);
  PosicionBase:
    u[base] == 1;
  forall(i in Lugares: i != base)
    Posicion:
      2 <= u[i] <= n;
}

execute {
  writeln("km = ", Km);
  var ruta = base;
  var actual = base;
  for (var paso = 1; paso <= n; paso++) {
    for (var j in Lugares)
      if (x[actual][j] > 0.5) { actual = j; break; }
    ruta = ruta + "-" + actual;
  }
  writeln("ruta = ", ruta);
  for (var i in Lugares)
    writeln("u[", i, "] = ", u[i]);
}
