# Ter Chat

Ter Chat — это простой терминал-чата с искусственным интеллектом, использующий API OpenRouter для общения с моделью DeepSeek Chat. Проект реализован на Python с интерфейсом в стиле TUI (Text User Interface) с помощью библиотеки `curses`.

## Возможности
- Потоковый вывод ответов от ИИ.
- Подсчет токенов с помощью `tiktoken`.
- Поддержка команд: `/reset`, `/help`, `/save`, `exit`.
- Цветной интерфейс в терминале.
- Сохранение истории чата в файл.

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш_логин/ter_chat.git
   cd ter_chat