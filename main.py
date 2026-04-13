import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from game_of_life import GameOfLife  # Importujemy nasz silnik gry
import numpy as np  # <-- ZMIANA 1: Zaimportowanie NumPy

# === Adnotacje (Wymagania) ===
GRID_WIDTH = 200  # Minimalny rozmiar: 200x200
GRID_HEIGHT = 200


def get_user_choice(prompt, min_val, max_val):
    """Bezpiecznie pobiera liczbę całkowitą od użytkownika w konsoli."""
    while True:
        try:
            choice = int(input(prompt))
            if min_val <= choice <= max_val:
                return choice
            else:
                print(f"Błąd: Wartość musi być pomiędzy {min_val} a {max_val}.")
        except ValueError:
            print("Błąd: Wprowadź poprawną liczbę całkowitą.")


def main():
    print("--- LAB 4: Gra w Życie (Automaty Komórkowe 2D) ---")

    # === Pobieranie ustawień od użytkownika ===
    bc_choice = get_user_choice(
        "Wybierz warunek brzegowy:\n 1. Periodyczny (zawijany)\n 2. Odbijający (stała granica)\nWybór: ", 1, 2)

    rs_choice = get_user_choice(
        "\nWybierz zestaw reguł:\n 1. Domyślne (Gra w Życie B3/S23)\n 2. Własna (HighLife B36/S23)\nWybór: ", 1, 2)

    p_choice = get_user_choice(
        "\nWybierz wzorzec początkowy:\n"
        " 1. Glider\n"
        " 2. Niezmienny (Krzyż)\n"
        " 3. Oscylator (Blinker)\n"
        " 4. Oscylator (Pulsar > 15)\n"
        " 5. Losowy chaos (20% wypelnienia)\n"
        "Wybór: ", 1, 5)

    # 1. Inicjalizacja silnika gry
    game = GameOfLife(GRID_WIDTH, GRID_HEIGHT)

    # 2. Ustawienie parametrów gry
    game.boundary_condition = 'periodic' if bc_choice == 1 else 'reflecting'
    game.rule_set = 'conway' if rs_choice == 1 else 'custom_highlife'

    # Mapowanie wyboru na nazwy wzorców
    patterns = {1: 'glider', 2: 'still_life_cross', 3: 'blinker', 4: 'pulsar'}

    if p_choice == 5:
        # Użytkownik wybrał losowe wypełnienie
        game.place_random(density=0.2)
    else:
        # Użytkownik wybrał standardowy wzorzec
        pattern_name = patterns[p_choice]
        start_x = GRID_WIDTH // 2 - 10
        start_y = GRID_HEIGHT // 2 - 10
        game.place_pattern(pattern_name, start_x, start_y)

    # 3. Inicjalizacja wizualizacji (Matplotlib)
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.canvas.manager.set_window_title("Gra w Życie (Python/Matplotlib)")

    img = ax.imshow(game.get_grid(), cmap='binary', interpolation='nearest')

    ax.set_xticks([])
    ax.set_yticks([])

    # --------------------------------------------------------------------
    # change 2: funkcja 'animate'
    # --------------------------------------------------------------------
    def animate(frame):
        """Funkcja wywoływana dla każdej klatki animacji."""
        game.update()  # Oblicz następny stan
        new_grid = game.get_grid()  # Pobierz nową siatkę

        # Zlicz żywe komórki (suma wszystkich '1' w siatce)
        live_cells = np.sum(new_grid)

        img.set_data(new_grid)  # Zaktualizuj obraz

        # Ustaw nowy tytuł z iteracją i liczbą komórek
        iteration = frame + 1
        ax.set_title(f"Iteracja: {iteration} | Żywe komórki: {live_cells}")

        return img,  # Zwracamy zaktualizowany obiekt

    anim = FuncAnimation(fig, animate,
                         frames=300, interval=50, blit=False, repeat=False)

    print("\nUruchomiono symulację. Otwórz okno Matplotlib...")
    plt.show()  # Pokaż okno z animacją


if __name__ == "__main__":
    main()
    #main