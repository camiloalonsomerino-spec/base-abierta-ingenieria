/*********************************************
 * Unidad 4 · Ejercicios 4.7 y 4.10
 * Localización de bodegas con costo fijo (UFL), acoplamiento desagregado.
 * Con capacidad y un solo proveedor por cliente: u04_e10_capacidad.mod.
 * Datos en u04_e07_bodegas.dat. Base abierta de ingeniería.
 *********************************************/

{string} Bodegas  = ...;
{string} Clientes = ...;

float fijo[Bodegas]              = ...;   // CLP al mes si se abre la bodega
float demanda[Clientes]          = ...;   // cajas al mes
float costo[Bodegas][Clientes]   = ...;   // CLP por caja despachada

dvar boolean y[Bodegas];                   // 1 si se abre la bodega i; 0 en otro caso
dvar float+  x[Bodegas][Clientes];         // fracción de la demanda de j que atiende i

dexpr float Costo = sum(i in Bodegas) fijo[i] * y[i]
                  + sum(i in Bodegas, j in Clientes) costo[i][j] * demanda[j] * x[i][j];

minimize Costo;

subject to {
  forall(j in Clientes)
    Atender:
      sum(i in Bodegas) x[i][j] == 1;
  forall(i in Bodegas, j in Clientes)
    Abierta:
      x[i][j] <= y[i];
}

execute {
  writeln("costo = ", Costo);
  for (var i in Bodegas)
    writeln("y[", i, "] = ", y[i]);
}
