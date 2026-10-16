/*********************************************
 * Unidad 4 · Ejercicio 4.10
 * Localización con capacidad y un solo proveedor por cliente.
 * Mismos datos que 4.7 más la capacidad: u04_e10_capacidad.dat.
 *********************************************/

{string} Bodegas  = ...;
{string} Clientes = ...;

float fijo[Bodegas]              = ...;   // CLP al mes si se abre la bodega
float demanda[Clientes]          = ...;   // cajas al mes
float costo[Bodegas][Clientes]   = ...;   // CLP por caja despachada
float cap[Bodegas]               = ...;   // cajas al mes que despacha la bodega

dvar boolean y[Bodegas];                   // 1 si se abre la bodega i; 0 en otro caso
dvar boolean x[Bodegas][Clientes];         // 1 si el cliente j se atiende desde i; 0 en otro caso

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
  forall(i in Bodegas)
    Capacidad:
      sum(j in Clientes) demanda[j] * x[i][j] <= cap[i] * y[i];
}

execute {
  writeln("costo = ", Costo);
  for (var i in Bodegas)
    writeln("y[", i, "] = ", y[i]);
}
