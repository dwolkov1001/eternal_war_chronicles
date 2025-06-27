import pygame

class Camera:
    """
    Класс Camera управляет смещением и масштабированием вида на игровую карту.
    Он позволяет игроку перемещаться по карте и изменять масштаб.
    """
    def __init__(self, width, height):
        """
        Инициализирует камеру.
        :param width: Ширина видимой области (viewport), к которой привязана камера.
        :param height: Высота видимой области (viewport).
        """
        self.width = width
        self.height = height
        # Смещение камеры в пикселях от верхнего левого угла мира.
        # Положительные значения сдвигают мир влево/вверх.
        self.x = 0
        self.y = 0
        # Уровень масштабирования. 1.0 = нормальный вид. >1.0 = приближение, <1.0 = отдаление.
        self.zoom = 1.0
        self.zoom_speed = 1.1 # Множитель для зума
        self.max_zoom = 5.0
        self.min_zoom = 0.45 # Рассчитано так, чтобы вся карта (1600px) помещалась в вид (720px)
        self.move_speed = 20

    def _clamp(self, map_width_pixels, map_height_pixels):
        """Ограничивает положение камеры границами мира."""
        max_x = map_width_pixels - self.width / self.zoom
        max_y = map_height_pixels - self.height / self.zoom

        # Если карта меньше вида по ширине, центрируем ее. Иначе — ограничиваем.
        if max_x < 0:
            self.x = max_x / 2
        else:
            self.x = max(0, min(self.x, max_x))

        # Если карта меньше вида по высоте, центрируем ее. Иначе — ограничиваем.
        if max_y < 0:
            self.y = max_y / 2
        else:
            self.y = max(0, min(self.y, max_y))

    def move(self, dx, dy, map_width_pixels, map_height_pixels):
        """
        Перемещает камеру на (dx, dy) с учетом границ мира.
        Скорость перемещения не зависит от зума.
        """
        self.x += dx / self.zoom
        self.y += dy / self.zoom
        self._clamp(map_width_pixels, map_height_pixels)

    def _zoom(self, zoom_factor, map_width_pixels, map_height_pixels):
        """Внутренний метод для масштабирования с центром в середине экрана."""
        # Где был центр мира до зума
        old_center_world_x = self.x + self.width / 2 / self.zoom
        old_center_world_y = self.y + self.height / 2 / self.zoom
        
        # Применяем зум
        self.zoom *= zoom_factor
        self.zoom = max(self.min_zoom, min(self.zoom, self.max_zoom))

        # Где центр мира стал после зума
        new_center_world_x = self.x + self.width / 2 / self.zoom
        new_center_world_y = self.y + self.height / 2 / self.zoom

        # Смещаем камеру, чтобы центр остался на месте
        self.x += old_center_world_x - new_center_world_x
        self.y += old_center_world_y - new_center_world_y

        # Немедленно проверяем границы после изменения координат
        self._clamp(map_width_pixels, map_height_pixels)

    def zoom_in(self, map_width_pixels, map_height_pixels):
        """Приближает вид."""
        self._zoom(self.zoom_speed, map_width_pixels, map_height_pixels)

    def zoom_out(self, map_width_pixels, map_height_pixels):
        """Отдаляет вид."""
        self._zoom(1 / self.zoom_speed, map_width_pixels, map_height_pixels) 