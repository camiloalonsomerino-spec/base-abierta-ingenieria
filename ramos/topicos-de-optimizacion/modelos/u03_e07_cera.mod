/*********************************************
 * Unidad 3 · Ejercicio 3.7
 * Compra de cera con descuento incremental: la función por partes de OPL
 * (piecewise). CPLEX agrega por su cuenta lo que haga falta para que la
 * función cóncava se cumpla. Datos en u03_e07_cera.dat.
 *********************************************/

float precio[1..3] = ...;   // CLP por kg en cada tramo
float corte[1..2]  = ...;   // kg acumulados donde cambia el precio
float compra       = ...;   // kg que hay que comprar

dvar float+ q;              // kg comprados

// pendiente 1 hasta corte[1], pendiente 2 hasta corte[2], pendiente 3 después; vale 0 en q = 0
dexpr float Costo = piecewise{precio[1] -> corte[1]; precio[2] -> corte[2]; precio[3]} q;

minimize Costo;

subject to {
  Necesidad:
    q >= compra;
}

execute {
  writeln("costo = ", Costo);
  writeln("q = ", q);
}
