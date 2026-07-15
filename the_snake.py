from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTR = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 15

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """
    Базовый класс для всех объектов игры, который содржит:
    body_color (tuple): Цвет объекта в формате RGB.
    position (tuple): Координаты объекта (x, y) на игровой сетке.
    """

    def __init__(self, body_color=None):
        self.body_color = body_color
        self.position = SCREEN_CENTR

    def draw(self, position=None, color=None):
        """Метод для отрисовки одной клетки на экране."""
        position = position if position is not None else self.position
        color = color if color is not None else self.body_color
        rect = (pg.Rect(position, (GRID_SIZE, GRID_SIZE)))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Класс змейки, отвечает за поведение, движение и отрисовку. Внутри:
    body_color (tuple): цвет змейки, наследуется от GameObject.
    direction (tuple): текущее направление движения змейки (вектор x, y).
    last (tuple): координаты последнего сегмента хвоста (для затирания).
    length (int): текущая длина змейки.
    next_direction (tuple): следующее направление движения от игрока.
    positions (list): список кортежей с координатами всех сегментов змейки.
    """

    def __init__(self):
        super().__init__(body_color=SNAKE_COLOR)
        self.reset(start_direction=RIGHT)

    def reset(self, start_direction=None):
        """
        Сбрасывает все данные змейки к начальному на страрте или проигрыше.
        Задаёт длину змейки в 1 клетку и определяется направление движения.
        """
        self.length = 1
        self.positions = [SCREEN_CENTR]
        if start_direction:
            self.direction = start_direction
        else:
            self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """
        Обновляет позицию змейки на игровом поле:
        Определяет положение головы по заданному направлению и удаляет хвост.
        Позволяет змейке двигаться через стены.
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        self.new_head_position = ((head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
                                  (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT)
        self.positions.insert(0, self.new_head_position)  # Добавдяем голову
        self.last = self.positions[-1]

        # Удаляем хвост, если длина змейки превышает self.length
        if len(self.positions) > self.length:
            del self.positions[-1]

    def update_direction(self):
        """
        Обновляет направление движения змейки
        на заданное пользователем следующее направление.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """
        Отрисовывает змейку на экране.
        Рисует новую голову и стирает ушедший сегмент хвоста.
        """
        for position in self.positions:
            super().draw(position=position, color=SNAKE_COLOR)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


class Apple(GameObject):
    """
    Класс яблока, отвечает за рандомное размещение и отрисовку. Внутри:
    body_color (tuple): цвет яблока, унаследованный от GameObject.
    Метод рисования яблока наследуется от родительского класса GameObject.
    """

    def __init__(self, snake_positions=None):
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(snake_positions)

    def randomize_position(self, snake_positions=None):
        """
        Создаёт случайные координаты (по сетке) яблока на игровом поле,
        исключая тело змейки.
        """
        if snake_positions is None:
            snake_positions = []
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_position = (x, y)
            if new_position not in snake_positions:
                self.position = new_position
                break


def handle_keys(game_object):
    """
    Считывает направление движения змейки с клавиатуры от пользователя,
    исключает возможность разворота змейки в противоположную сторону.
    Позволяет корректно завершить программу.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            elif event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def update_score(length):
    """Отображает в заголовке окна игры актуальный счёт."""
    pg.display.set_caption(f"Змейка | Счёт: {length} | Выход: ESC")


def main():
    """
    Основная функция запуска игры.
    Инициализирует модули Pygame, создает игровые объекты,
    запускает главный цикл игры.
    """
    # Инициализация PyGame
    pg.init()
    # Экземпляры классов
    snake = Snake()
    apple = Apple(snake.positions)
    # Очищаем экран черным цветом один раз при старте игры
    screen.fill(BOARD_BACKGROUND_COLOR)
    # Добавляем первое яблоко на экран
    apple.draw()
    update_score(snake.length)

    running = True
    while running:
        clock.tick(SPEED)  # Ограничение скорости игры

        handle_keys(snake)  # Обработка нажатия клавиш

        # Обновление состояния змейки
        snake.update_direction()
        snake.move()

        # Проверка на столкновение змейки с самой собой
        if snake.get_head_position() in snake.positions[4:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(snake.positions)
            apple.draw()
            update_score(snake.length)

        # Отрисовка объектов на экране:
        # Проверка, съела ли змейка яблоко,
        # если да - увеличиваем длину, обновляем счёт игры
        # и создаём новое яблоко.
        elif snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
            apple.draw()
            update_score(snake.length)
        # Рисуем змейку
        snake.draw()

        # Обновляем окно игры, чтобы показать изменения
        pg.display.update()

    # Деинициализирует все модули Pygame, которые были инициализированы ранее
    pg.quit()


if __name__ == '__main__':
    main()
