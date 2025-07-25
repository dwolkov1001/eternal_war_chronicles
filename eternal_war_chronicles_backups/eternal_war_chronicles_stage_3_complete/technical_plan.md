# Технический план разработки (детализированный)
## Проект: "Хроники Вечной Войны"

---

### Введение

Этот документ описывает поэтапный план разработки проекта "Хроники Вечной Войны". Этапы выстроены в логическом порядке, от создания фундаментальных механик к добавлению более сложных систем и контента. Каждый этап содержит детализированные задачи и шаги по контролю качества для обеспечения ясного и последовательного процесса разработки.

---

### Этап 1: Ядро и архитектура

**Цель:** Создать базовую структуру проекта и заложить основу для всех будущих механик.

1.  **Настройка проекта:** `[ВЫПОЛНЕНО]`
    *   Создание структуры папок: `src/` (с подпапками `core`, `ai`, `ui`, `game_objects`), `tests/`.
    *   Инициализация репозитория `git`.
    *   Создание файла `main.py` - точки входа в приложение.
2.  **Движок игры:** `[ВЫПОЛНЕНО]`
    *   В `main.py`: инициализация `Pygame`.
    *   Создание класса `Game` в `src/core/game.py`, отвечающего за главный игровой цикл (main loop).
    *   Реализация обработки базовых событий (выход из игры).
3.  **Управление временем и календарь:** `[ОСНОВА ЗАЛОЖЕНА]`
    *   В классе `Game`: внедрение `pygame.time.Clock` для контроля FPS.
    *   Создание в `Game` переменных-заглушек для паузы и ускорения времени (`paused`, `time_multiplier`).
    *   Создание в `GameWorld` переменной-заглушки для отслеживания времени (`current_time`).
4.  **Базовые классы:** `[ВЫПОЛНЕНО]`
    *   `src/game_objects/unit.py`: `Unit` (атрибуты: `hp`, `attack`, `defense`).
    *   `src/game_objects/army.py`: `Army` (атрибуты: список `units`, `position`).
    *   `src/game_objects/faction.py`: `Faction` (атрибуты: список `armies`, `color`, `name`).
    *   `src/core/world.py`: `GameWorld` (атрибуты: `map_data`, список `factions`, `current_time`).
5.  **Система рендеринга:** `[ВЫПОЛНЕНО]`
    *   В `src/core/renderer.py`: класс `Renderer` с методом `render(world, screen)`, который пока ничего не отрисовывает, но вызывается в главном цикле.

**Сопутствующие задачи:**
*   **Тестирование:** Проверить, что игровой цикл стабилен, время ускоряется/замедляется и ставится на паузу корректно, а внутриигровой календарь правильно считает дни и сезоны.
*   **Документация:** Написать докстринги для базовых классов (`Game`, `GameWorld`, `Army` и т.д.).

**Результат этапа:** Чёрный экран, работающий игровой цикл, управление временем через консоль/клавиши. В памяти создаются и существуют базовые объекты игры и система календаря.

---

### Этап 2: Мир и карта `[ЗАВЕРШЕН]`

**Цель:** Сделать мир видимым и интерактивным.

1.  **Процедурная генерация карты:** `[ВЫПОЛНЕНО]`
    *   В `src/core/map_generator.py`: функция `generate_map(width, height)`, использующая, например, шум Перлина для создания 2D-массива тайлов.
    *   Определение базовых типов тайлов: `GRASS`, `WATER`, `MOUNTAIN`, `FOREST`.
2.  **Визуализация карты:** `[ВЫПОЛНЕНО]`
    *   В `Renderer`: метод `render_map(map_data, screen)` для отрисовки тайлов.
    *   Отрисовка тайлов цветными прямоугольниками, генерируемыми, в зависимости от типа ландшафта.
3.  **Камера:** `[ВЫПОЛНЕНО]`
    *   В `src/core/camera.py`: класс `Camera` с атрибутами `x`, `y`, `zoom`.
    *   Реализация методов `move(dx, dy)` и `zoom_in/out()`.
    *   Интеграция камеры в `Renderer` для отрисовки только видимой части карты.

**Сопутствующие задачи:**
*   **Тестирование:** `[ВЫПОЛНЕНО]` Проверить, что камера плавно движется и масштабируется, не выходит за границы карты.
*   **Документация:** `[ВЫПОЛНЕНО]` Написать докстринги для класса `Camera`.

**Результат этапа:** Отображается игровая карта, которую можно исследовать с помощью перемещения и масштабирования камеры. Производительность стабильна.

---

### Этап 3: Базовые механики армий и юнитов

**Цель:** "Оживить" карту, добавив на неё движущиеся объекты.

1.  **Рендеринг армий:** `[ВЫПОЛНЕНО]`
    *   В `Renderer`: метод `render_armies(armies, screen, camera)`, отображающий армии в виде цветных кругов на их координатах.
2.  **Перемещение:** `[ВЫПОЛНЕНО]`
    *   Интеграция библиотеки для поиска пути, например, `pathfinding`. `[ОТЛОЖЕНО]` - реализовано прямолинейное движение.
    *   В классе `Army`: метод `set_destination(x, y)`, который рассчитывает путь и сохраняет его. `[ВЫПОЛНЕНО]`
    *   В главном цикле: обновление позиций армий вдоль рассчитанного пути с учётом `time_multiplier`. `[ВЫПОЛНЕНО]`
3.  **Управление для тестов:** `[ВЫПОЛНЕНО]`
    *   Реализация обработки кликов мыши для выбора армии и задания ей точки назначения.

**Сопутствующие задачи:**
*   **Тестирование:** Проверить корректность работы pathfinding-а на разных ландшафтах, убедиться, что армии следуют приказам и не проходят сквозь непроходимые тайлы. `[ОТЛОЖЕНО]`
*   **Временная графика:** Создать простые иконки или спрайты для армий разных фракций, чтобы их можно было различать.

**Результат этапа:** Реализована возможность кликать по армиям и задавать им цель, после чего они плавно перемещаются по карте к указанной точке.

---

### Этап 4: Базовая боевая система

**Цель:** Реализовать ключевой элемент игры — столкновение армий.

1.  **Обнаружение столкновений:**
    *   В главном цикле: проверка расстояний между армиями враждующих фракций.
    *   При сближении на определённое расстояние — запуск боя.
2.  **Расчёт боя:**
    *   В `src/core/combat.py`: функция `resolve_combat(army1, army2)`, которая суммирует `attack` и `defense` всех юнитов и определяет победителя.
3.  **Визуализация и логи:**
    *   После боя проигравшая армия удаляется из списка фракции.
    *   В консоль выводится лог: "Армия [X] победила армию [Y] в [день/месяц/год]".

**Сопутствующие задачи:**
*   **Тестирование:** Запустить несколько тестовых боев с разными составами армий, проверить корректность расчётов и удаления проигравшего.
*   **Документация:** Описать функцию `resolve_combat` и формат данных, которые она возвращает.

**Результат этапа:** Армии могут сражаться и исчезать с карты. Появляется первая версия игрового цикла "перемещение -> бой".

---

### Этап 5: Начальный ИИ-генерал

**Цель:** Сделать мир автономным, передав управление армиями ИИ.

1.  **Класс `GeneralAI`:**
    *   В `src/ai/general_ai.py`: класс `GeneralAI` с методом `update(world, army)`.
2.  **Простейшая логика:**
    *   Внутри `update`: найти ближайшую вражескую армию и вызвать у своей армии `set_destination` на её позицию.
3.  **Интеграция:**
    *   В классе `Faction`: создание и привязка экземпляров `GeneralAI` к каждой армии.
    *   В главном цикле: вызов метода `update` для каждого ИИ-генерала.

**Сопутствующие задачи:**
*   **Тестирование:** Наблюдать за поведением ИИ в течение длительного времени, убедиться, что он не зависает, не создаёт "пробок" из армий и принимает базовые решения.
*   **Рефакторинг:** Отделить логику ИИ от основного игрового цикла, чтобы их можно было развивать независимо.

**Результат этапа:** Игра может "играть сама в себя". Армии под управлением ИИ перемещаются по карте и сражаются друг с другом. Тестовое управление от игрока отключается.

---

### Этап 6: Расширение мира и разнообразия

**Цель:** Добавить тактическую глубину в существующие механики.

1.  **Подтипы ландшафтов и юнитов:**
    *   Расширение классов `Tile` и `Unit` для поддержки всех подтипов и их характеристик (бонусы/штрафы к скорости, атаке, защите).
    *   Обновление генератора карт для создания более разнообразного мира.
2.  **Усложнение боевой системы:**
    *   Переработка `resolve_combat`: теперь она должна учитывать бонусы от ландшафта и систему контр-юнитов (например, кавалерия получает штраф в лесу, копейщики наносят доп. урон кавалерии).

**Сопутствующие задачи:**
*   **Тестирование:** Провести тесты боевой системы с учётом всех новых юнитов и ландшафтов, проверить все бонусы и штрафы.
*   **Балансировка:** Сделать первую грубую настройку характеристик юнитов, чтобы не было явных имбалансных стратегий.

**Результат этапа:** Бои становятся более тактическими. Победа зависит от правильного использования местности и состава армии.

---

### Этап 7: Обучение и принятие решений ИИ

**Цель:** Сделать ИИ "умным" и обучаемым.

1.  **База знаний и история:**
    *   В `GeneralAI`: добавление `knowledge_base` (словарь для хранения фактов) и `decision_history` (список принятых решений).
2.  **Система обучения:**
    *   Создание системы весов для тактик (например, `tactic_weights = {'charge': 0.5, 'flank': 0.3, 'defend': 0.2}`).
    *   После боя — вызов функции `learn_from_battle`, которая корректирует веса в зависимости от исхода и контекста.
3.  **Контекстное принятие решений:**
    *   `update` ИИ теперь анализирует ландшафт и состав армии, выбирая тактику с наивысшим весом для текущей ситуации.

**Сопутствующие задачи:**
*   **Тестирование:** Создать тестовые сценарии, чтобы проверить, меняется ли поведение ИИ после серии побед/поражений в одинаковых условиях.
*   **Логирование:** Улучшить логирование, чтобы видеть, почему ИИ принял то или иное решение и как изменились его веса после боя.

**Результат этапа:** ИИ-генералы начинают вести себя по-разному и адаптироваться к результатам прошлых боёв.

---

### Этап 8: Тактическое управление (Система отрядов)

**Цель:** Дать ИИ-генералам возможность разделять свои армии на более мелкие тактические единицы (отряды) для выполнения специализированных задач, что станет практическим проявлением их "интеллекта".

1.  **Рефакторинг архитектуры:**
    *   Создание класса `Detachment` (Отряд), который становится основной движущейся единицей на карте.
    *   Изменение класса `Army`, который теперь выступает как организационная структура, управляющая своими отрядами.
    *   Адаптация боевой системы для столкновений между отрядами.
2.  **Логика ИИ для управления отрядами:**
    *   Реализация базовых сценариев: создание разведывательных отрядов, авангарда, разделение сил для атаки с разных направлений.
    *   Интеграция с системой обучения: генерал учится, какие тактики с использованием отрядов приносят успех.
3.  **Обратная связь для игрока:**
    *   Визуальное отображение отрядов на карте.
    *   Добавление информации об отрядах в отчеты генерала.
    *   Возможность для игрока давать советы по управлению отрядами через NLP-интерфейс.

**Сопутствующие задачи:**
*   **Тестирование:** Создать сценарии, где разделение сил дает явное преимущество, и проверить, сможет ли ИИ это использовать.
*   **Визуализация:** Разработать понятное отображение связи между армией-контейнером и её отрядами.

**Результат этапа:** ИИ-генералы действуют более реалистично и тактически гибко. Игрок может наблюдать за их решениями и влиять на них, что углубляет геймплей.

---

### Этап 9: Механики игрока-"бога"

**Цель:** Реализовать основной геймплей со стороны игрока.

1.  **Погода и катастрофы:**
    *   Создание системы погоды (`WeatherSystem`), которая меняет глобальные модификаторы.
    *   Реализация UI-кнопок для игрока, чтобы вызывать дождь, туман и т.д.
2.  **NLP-модуль:**
    *   Интеграция `spaCy`. Создание функции `parse_player_message(text)`, которая извлекает сущности.
    *   Метод `inject_information` у `GeneralAI` для добавления этих фактов в `knowledge_base`.
3.  **Интерфейс взаимодействия:**
    *   Создание текстового поля для ввода сообщений, UI для допроса генерала (вызывает его метод `generate_report`).
    *   Реализация обратной связи, показывающей, как ИИ интерпретировал команду игрока.

**Сопутствующие задачи:**
*   **Тестирование:** Протестировать все способы влияния игрока: погода, катастрофы, ввод текста. Проверить, что ИИ корректно реагирует на полученную информацию.
*   **Документация:** Описать API для NLP-модуля и системы событий, чтобы их было легко расширять.

**Результат этапа:** Реализована возможность для игрока активно влиять на мир и поведение ИИ.

---

### Этап 10: Снабжение, логистика и экономика

**Цель:** Добавить стратегический слой управления ресурсами.

1.  **Расходники и обозы:**
    *   Добавление в класс `Army` атрибутов для всех типов расходников: `food`, `ammo`, `supplies` (медикаменты, материалы для починки брони и оружия).
    *   Создание юнита `SupplyWagon`. Армии расходуют ресурсы каждый ход.
2.  **Экономика фракций:**
    *   Города и деревни получают атрибут `production` (еда, золото).
    *   Фракции могут тратить ресурсы на найм новых юнитов.
3.  **Истощение (Attrition):**
    *   Если у армии заканчивается еда, она начинает терять юнитов каждый ход.

**Сопутствующие задачи:**
*   **Тестирование:** Проверить, что ресурсы корректно производятся и тратятся, а истощение правильно работает.
*   **Балансировка:** Настроить скорость потребления ресурсов и их производство, чтобы избежать быстрого коллапса или бесконечного накопления.

**Результат этапа:** Победа зависит не только от тактики, но и от стратегии и логистики.

---

### Этап 11: Продвинутые механики

**Цель:** Добавить оставшиеся системы для полноты игрового опыта.

1.  **Спец. отряды и осадные машины:**
    *   Реализация уникальных действий: `Engineer.build_fort()`, `Spy.sabotage()`.
    *   Добавление классов для осадных машин: `Catapult`, `BatteringRam` и их интеграция в боевую систему.
2.  **Мораль и дезертирство:**
    *   Добавление атрибута `morale` в класс `Army`.
    *   Мораль меняется после боёв, из-за голода или событий. При низкой морали — шанс дезертирства.
3.  **Герои и события:**
    *   Создание `EventSystem`, которая может генерировать случайные события.
    *   Реализация класса `Hero` с уникальными пассивными или активными способностями.

**Сопутствующие задачи:**
*   **Тестирование:** Создать ситуации для проверки работы спец. отрядов, морали, дезертирства и случайных событий.
*   **Интеграция:** Убедиться, что все новые механики гармонично работают друг с другом (например, герой-лидер повышает мораль и снижает шанс дезертирства).

**Результат этапа:** Игра становится более глубокой и реиграбельной.

---

### Этап 12: Интерфейс и полировка

**Цель:** Сделать игру удобной и приятной для игрока.

1.  **Главное меню и UI:**
    *   Создание сцен: `MainMenuScene`, `GameScene`, `SettingsScene`.
    *   Реализация сохранения/загрузки игры (сериализация состояния `GameWorld`).
    *   Добавление на игровой экран виджетов календаря и часов.
2.  **Информационные панели:**
    *   Создание UI-элементов для отображения логов, докладов ИИ, внутриигрового справочника (энциклопедии) и каталога генералов с их наследием.
3.  **Визуальная полировка:**
    *   Переход от временной геометрической графики к более сложной и проработанной процедурной отрисовке юнитов, армий и элементов ландшафта.
    *   Добавление процедурных визуальных эффектов для ключевых событий (смена погоды, бои, катаклизмы).
4.  **Балансировка и отладка:**
    *   Интенсивное тестирование, исправление багов, настройка всех числовых параметров.

**Сопутствующие задачи:**
*   **Пользовательское тестирование (Playtesting):** Предоставить прототип для тестирования нескольким людям, чтобы собрать отзывы об удобстве интерфейса и понятности механик.
*   **Оптимизация:** Профилировать код, найти и устранить узкие места в производительности, особенно в рендеринге и логике ИИ.

**Результат этапа:** Полноценный, отполированный продукт.

---

### Этап 13: Контент и расширяемость

**Цель:** Обеспечить долгосрочную поддержку и реиграбельность.

1.  **Сценарии и достижения:**
    *   Создание системы для запуска игры с предопределёнными условиями.
    *   Реализация системы отслеживания и отображения достижений генералов.
2.  **Поддержка модов:**
    *   Рефакторинг кода для загрузки данных (юниты, ландшафты, правила) из внешних JSON или YAML файлов.
3.  **Наполнение контентом:**
    *   Написание текстов для энциклопедии, докладов, сценариев.

**Сопутствующие задачи:**
*   **Тестирование модов:** Проверить механизм загрузки модов на примере нескольких тестовых модов.
*   **Документация для моддеров:** Написать руководство по созданию модов для игры.

**Результат этапа:** Готовая к релизу игра с возможностью расширения силами сообщества. 