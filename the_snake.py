from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """
    Базовый класс для всех объектов игры, который содржит:
    body_color (tuple): Цвет объекта в формате RGB.
    position (tuple): Координаты объекта (x, y) на игровой сетке.
    """

    def __init__(self, body_color=None):
        self.body_color = body_color
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def draw(self):
        """
        Метод для отрисовки объектана экране,
        переопределяется в дочерних классах.
        """
        pass


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
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
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
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """
        Сбрасывает все данные змейки к начальному при проигрыше.
        Очищает игровое поле, сбрасывает длину змейки до 1
        и выбирает случайное направление движения при старте.
        """
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None


class Apple(GameObject):
    """
    Класс яблока, отвечает за рандомное размещение и отрисовку. Внутри:
    body_color (tuple): цвет яблока, унаследованный от GameObject.
    """

    def __init__(self):
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Создаёт случайные координаты (по сетке) яблока на игровом поле."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self):
        """Отрисовывает яблоко в одну ячейку сетки по координатам."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(game_object):
    """
    Считывает направление движения змейки с клавиатуры от пользователя,
    исключает возможность разворота змейки в противоположную сторону.
    Позволяет корректно завершить программу.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Основная функция запуска игры.
    Инициализирует модули Pygame, создает игровые объекты,
    запускает главный цикл игры.
    """
    # Инициализация PyGame
    pygame.init()
    # Экземпляры классов
    snake = Snake()
    apple = Apple()
    # Очищаем экран черным цветом один раз при старте игры
    snake.reset()
    # Добавляем первое яблоко на экран
    apple.draw()

    running = True
    while running:
        clock.tick(SPEED)  # Ограничение скорости игры

        handle_keys(snake)  # Обработка нажатия клавиш

        # Обновление состояния змейки
        snake.update_direction()
        snake.move()

        # Проверка на столкновение змейки с самой собой
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position()
            apple.draw()

        # Отрисовка объектов на экране:
        # Проверка, съела ли змейка яблоко,
        # если да - увеличиваем длину и создаём новое яблоко.
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()
            apple.draw()
        # Рисуем змейку
        snake.draw()

        # Обновляем окно игры, чтобы показать изменения
        pygame.display.update()

    # Деинициализирует все модули Pygame, которые были инициализированы ранее
    pygame.quit()


if __name__ == '__main__':
    main()
