/*********************************************
 * Unidad 8 · Ruta más corta como flujo de costo mínimo
 * Una unidad de flujo sale del origen y llega al destino.
 * Datos en u08_ruta_mas_corta.dat. Base abierta de ingeniería.
 *********************************************/

// CONJUNTOS Y PARÁMETROS
tuple Camino { string i; string j; int km; }
{string} Nodos   = ...;
{Camino} Caminos = ...;                 // caminos de doble sentido, con su largo
string origen    = ...;
string destino   = ...;

// Cada camino de doble sentido son dos arcos, uno en cada sentido
{Camino} Arcos = {<c.i, c.j, c.km> | c in Caminos} union {<c.j, c.i, c.km> | c in Caminos};

// Oferta de cada nodo: 1 en el origen, -1 en el destino, 0 en el resto
int b[n in Nodos] = (n == origen) ? 1 : ((n == destino) ? -1 : 0);

// VARIABLES DE DECISIÓN
dvar boolean x[Arcos];                  // 1 si la ruta usa el arco (i, j); 0 en otro caso

// EXPRESIONES
dexpr int Km = sum(a in Arcos) a.km * x[a];

// OBJETIVO
minimize Km;

// RESTRICCIONES
subject to {
  forall(n in Nodos)
    Balance:                            // lo que sale menos lo que entra = oferta del nodo
      sum(a in Arcos: a.i == n) x[a] - sum(a in Arcos: a.j == n) x[a] == b[n];
}

// SALIDA: solo los arcos que usa la ruta
execute {
  writeln("km = ", Km);
  for (var a in Arcos)
    if (x[a] > 0.5)
      writeln("x[", a.i, ",", a.j, "] = ", x[a]);
}
