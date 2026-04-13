import numpy as np
from scipy.signal import convolve2d


class GameOfLife:
    """
    Implementuje silnik "Gry w Życie" Conwaya.

    Używa NumPy do przechowywania siatki i SciPy.convolve2d do
    bardzo wydajnego obliczania sąsiadów (zamiast pętli for).
    """

    def __init__(self, width, height):
        """
        Inicjalizuje siatkę gry o podanych wymiarach.
        """
        self.width = width
        self.height = height
        # Siatka: 1 = żywa, 0 = martwa. Typ uint8 jest oszczędny pamięciowo.
        self.grid = np.zeros((height, width), dtype=np.uint8)

        # Jądro (kernel) konwolucji do zliczania sąsiadów.
        # [[1, 1, 1],
        #  [1, 0, 1],  <- "0" oznacza, że nie liczymy samej siebie
        #  [1, 1, 1]]
        self.kernel = np.array([[1, 1, 1],
                                      [1, 0, 1],
                                      [1, 1, 1]], dtype=np.uint8)

        # Domyślne ustawienia
        self.boundary_condition = 'periodic'  # 'periodic' lub 'reflecting'
        self.rule_set = 'conway'  # 'conway' lub 'custom_highlife'

    def _set_cell(self, x, y, alive):
        """Pomocnicza funkcja do bezpiecznego ustawiania komórek wzorca."""
        if 0 <= x < self.width and 0 <= y < self.height:
            # W NumPy [y, x] to standard (wiersz, kolumna)
            self.grid[y, x] = 1 if alive else 0

    def place_pattern(self, pattern_name, x, y):
        """
        Umieszcza wybrany wzorzec na siatce, czyszcząc poprzedni stan.
        === zad 2: Implementacja stanów początkowych ===
        """
        self.grid.fill(0)  # Czyścimy siatkę

        if pattern_name == 'glider':
            # Implementacja 5-komórkowego "Szybowca"
            self._set_cell(x + 1, y, True)
            self._set_cell(x + 2, y + 1, True)
            self._set_cell(x, y + 2, True)
            self._set_cell(x + 1, y + 2, True)
            self._set_cell(x + 2, y + 2, True)

        elif pattern_name == 'still_life_cross':  # Niezmienny (Krzyż)
            # Implementacja 5-komórkowego "Niezmiennego" krzyża
            self._set_cell(x + 1, y, True)
            self._set_cell(x, y + 1, True)
            self._set_cell(x + 1, y + 1, True)
            self._set_cell(x + 2, y + 1, True)
            self._set_cell(x + 1, y + 2, True)

        elif pattern_name == 'blinker':  # Oscylator prosty
            # Implementacja 3-komórkowego "Oscylatora prostego"
            self._set_cell(x, y, True)
            self._set_cell(x + 1, y, True)
            self._set_cell(x + 2, y, True)

        elif pattern_name == 'pulsar':  # Oscylator > 15 komórek
            # Implementacja "Pulsara" (okres 3), 48 komórek
            offsets = [2, 3, 4, 8, 9, 10]
            for offset in offsets:
                self._set_cell(x + offset, y, True)
                self._set_cell(x + offset, y + 5, True)
                self._set_cell(x + offset, y + 7, True)
                self._set_cell(x + offset, y + 12, True)

                self._set_cell(x, y + offset, True)
                self._set_cell(x + 5, y + offset, True)
                self._set_cell(x + 7, y + offset, True)
                self._set_cell(x + 12, y + offset, True)

    def place_random(self, density=0.2):
        """
        Wypełnia siatkę losowo, z zadanym prawdopodobieństwem (density).
        Na przykład 0.2 oznacza, że ok. 20% komórek będzie żywych.
        """
        # Tworzy siatkę losowych liczb (0.0 do 1.0)
        random_grid = np.random.rand(self.height, self.width)
        # Ustawia komórkę na żywą (1) jeśli jej losowa wartość jest mniejsza niż 'density'
        self.grid = (random_grid < density).astype(np.uint8)

    def update(self):
        """Oblicza następną generację komórek."""

        # === zad 3 i 4: Warunki brzegowe ===
        boundary_mode = 'wrap' if self.boundary_condition == 'periodic' else 'fill'

        # 'fill' z fillvalue=0 jest równoznaczne warunkowi 'odbijającemu'
        # (lub 'absorbującemu'), gdzie komórki poza siatką są martwe.

        # Oblicz liczbę sąsiadów dla KAŻDEJ komórki naraz za pomocą konwolucji 2D
        neighbors = convolve2d(self.grid, self.kernel,
                               mode='same',
                               boundary=boundary_mode,
                               fillvalue=0)

        # Stwórz maski logiczne (boolowskie) dla żywych i martwych komórek
        alive = (self.grid == 1)
        dead = (self.grid == 0)

        # === ZADANIE 1 i 5: Aplikacja reguł ===

        if self.rule_set == 'conway':
            # === zad1: Reguły Conwaya (B3/S23) ===
            # 1. Narodziny (Birth): Martwa (dead) komórka z 3 sąsiadami ożywa.
            birth = dead & (neighbors == 3)

            # 2. Przeżycie (Survival): Żywa (alive) komórka z 2 lub 3 sąsiadami przeżywa.
            survival = alive & ((neighbors == 2) | (neighbors == 3))

        elif self.rule_set == 'custom_highlife':
            # === zad5: Własna reguła (HighLife B36/S23) ===
            # 1. Narodziny: Martwa komórka z 3 LUB 6 sąsiadami ożywa.
            birth = dead & ((neighbors == 3) | (neighbors == 6))

            # 2. Przeżycie: Żywa komórka z 2 lub 3 sąsiadami przeżywa.
            survival = alive & ((neighbors == 2) | (neighbors == 3))

        # Zaktualizuj siatkę:
        # Najpierw wyzeruj całą siatkę...
        self.grid.fill(0)
        # ...a potem ustaw na 1 tylko te komórki, które urodziły się LUB przeżyły.
        self.grid[birth | survival] = 1

    def get_grid(self):
        """Zwraca obecny stan siatki (dla wizualizacji)."""
        return self.grid