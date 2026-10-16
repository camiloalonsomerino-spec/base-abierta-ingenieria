/*********************************************
 * Unidad 7 · Ejercicio 7.10
 * Árbol de expansión mínima con tope de grado en un nodo (puertos de la central).
 * Datos en u07_e10_grado.dat. Base abierta de ingeniería.
 *********************************************/

tuple Arista { string i; string j; int km; }
{string} Nodos   = ...;
{Arista} Aristas = ...;                 // metros de cable de cada enlace posible
string centro    = ...;                 // el nodo con tope de grado
int puertos      = ...;                 // cuántas aristas puede tener ese nodo

int N = card(Nodos);
range Subconjuntos = 1..ftoi(pow(2, N)) - 1;
int en[s in Subconjuntos][n in Nodos] = (s div ftoi(pow(2, ord(Nodos, n)))) mod 2;
int tam[s in Subconjuntos] = sum(n in Nodos) en[s][n];

dvar boolean x[Aristas];                // 1 si el enlace se tiende; 0 en otro caso

dexpr int Largo = sum(e in Aristas) e.km * x[e];

minimize Largo;

subject to {
  Total:
    sum(e in Aristas) x[e] == N - 1;
  forall(s in Subconjuntos: tam[s] >= 3)
    SinCiclos:
      sum(e in Aristas) en[s][e.i] * en[s][e.j] * x[e] <= tam[s] - 1;
  Grado:                                // la restricción nueva: a lo más «puertos» enlaces en la central
    sum(e in Aristas: e.i == centro || e.j == centro) x[e] <= puertos;
}

execute {
  writeln("largo = ", Largo);
  for (var e in Aristas)
    writeln("x[", e.i, ",", e.j, "] = ", x[e]);
}
