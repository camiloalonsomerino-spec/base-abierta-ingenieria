/*********************************************
 * Unidad 7 · Árbol de expansión mínima como programa entero
 * Una restricción de «sin ciclos» por cada subconjunto de 3 o más nodos.
 * Datos en u07_arbol_minimo.dat (caso) o u07_e05_cuatro_nodos.dat.
 * Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS Y PARÁMETROS
tuple Arista { string i; string j; int km; }
{string} Nodos   = ...;
{Arista} Aristas = ...;                 // cada arista con su largo (o costo)

int N = card(Nodos);

// Los subconjuntos de nodos se numeran de 1 a 2^N - 1: el bit k del número
// dice si el nodo k (en el orden de Nodos) está en el subconjunto.
range Subconjuntos = 1..ftoi(pow(2, N)) - 1;
int en[s in Subconjuntos][n in Nodos] = (s div ftoi(pow(2, ord(Nodos, n)))) mod 2;
int tam[s in Subconjuntos] = sum(n in Nodos) en[s][n];

// VARIABLES DE DECISIÓN
dvar boolean x[Aristas];                // 1 si la arista entra al árbol; 0 en otro caso

// EXPRESIONES
dexpr int Largo = sum(e in Aristas) e.km * x[e];

// OBJETIVO
minimize Largo;

// RESTRICCIONES
subject to {
  Total:                                // un árbol de N nodos tiene N - 1 aristas
    sum(e in Aristas) x[e] == N - 1;

  forall(s in Subconjuntos: tam[s] >= 3)
    SinCiclos:                          // dentro de S caben a lo más |S| - 1 aristas
      sum(e in Aristas) en[s][e.i] * en[s][e.j] * x[e] <= tam[s] - 1;
}

// SALIDA
execute {
  writeln("largo = ", Largo);
  for (var e in Aristas)
    writeln("x[", e.i, ",", e.j, "] = ", x[e]);
}
