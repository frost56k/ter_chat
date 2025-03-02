import os
from dotenv import load_dotenv
import tiktoken
import requests
import json
import curses

def stream_response(api_key, messages, history_win):
    """Функция для потокового вывода ответа в окно curses."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://example.com",
                "X-Title": "Ter Chat",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat:free",
                "messages": messages,
                "stream": True
            }),
            stream=True
        )

        if response.status_code != 200:
            history_win.addstr(f"Ошибка HTTP: {response.status_code} - {response.reason}\n")
            history_win.refresh()
            return None

        full_reply = ""
        history_win.addstr("ИИ: ")
        history_win.refresh()
        for chunk in response.iter_lines():
            if chunk:
                chunk_str = chunk.decode("utf-8").strip()
                if chunk_str == "data: [DONE]":
                    history_win.addstr("\n")
                    history_win.refresh()
                    return full_reply
                if chunk_str.startswith("data: "):
                    json_str = chunk_str[len("data: "):]
                    chunk_data = json.loads(json_str)
                    if "choices" in chunk_data:
                        chunk_content = chunk_data["choices"][0]["delta"].get("content", "")
                        history_win.addstr(chunk_content)
                        history_win.refresh()
                        full_reply += chunk_content
        history_win.addstr("\n")
        history_win.refresh()
        return full_reply

    except Exception as e:
        history_win.addstr(f"Ошибка: {str(e)}\n")
        history_win.refresh()
        return None

def count_tokens(text, model="gpt-3.5-turbo"):
    """Подсчет токенов в тексте."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def chat_interface(stdscr):
    # Инициализация цветов в curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Зелёный для системных сообщений
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Голубой для сообщений пользователя
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Жёлтый для токенов
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Красный для ошибок

    GREEN = curses.color_pair(1)
    CYAN = curses.color_pair(2)
    YELLOW = curses.color_pair(3)
    RED = curses.color_pair(4)

    # Загрузка API-ключа
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        stdscr.addstr(0, 0, "API-ключ не найден. Введите его: ")
        stdscr.refresh()
        api_key = stdscr.getstr().decode("utf-8").strip()
        if not api_key:
            stdscr.addstr(1, 0, "API-ключ обязателен. Нажмите любую клавишу для выхода.", RED)
            stdscr.refresh()
            stdscr.getch()
            return

    # Инициализация окон
    curses.curs_set(1)  # Включаем курсор
    height, width = stdscr.getmaxyx()
    if height < 5 or width < 20:
        stdscr.addstr(0, 0, "Терминал слишком маленький. Увеличьте окно.", RED)
        stdscr.refresh()
        stdscr.getch()
        return

    history_win = curses.newwin(height - 3, width, 0, 0)  # Окно истории
    input_win = curses.newwin(3, width, height - 3, 0)    # Окно ввода
    history_win.scrollok(True)

    # Начальные сообщения
    messages = [{"role": "system", "content": "Вы дружелюбный помощник. Отвечайте на русском языке."}]
    history_win.addstr("Добро пожаловать в чат с ИИ!\n", GREEN)
    history_win.addstr("Введите 'exit' для выхода, '/help' для команд.\n", YELLOW)
    history_win.refresh()

    while True:
        try:
            # Очистка и подготовка окна ввода
            input_win.clear()
            input_win.addstr(0, 0, "Вы: ")
            input_win.refresh()

            # Активируем ввод
            input_win.keypad(True)
            curses.echo()
            user_input = input_win.getstr(0, 4, 100).decode("utf-8").strip()
            curses.noecho()

            # Выводим в историю
            history_win.addstr(f"Вы: {user_input}\n", CYAN)
            history_win.refresh()

            # Обработка команд
            if user_input.lower() == "/reset":
                messages = messages[:1]
                history_win.addstr("История диалога очищена.\n", GREEN)
            elif user_input.lower() == "/help":
                history_win.addstr("Команды: /reset, /help, /save, exit\n", YELLOW)
            elif user_input.lower() == "/save":
                with open("chat_history.txt", "w", encoding="utf-8") as f:
                    for msg in messages:
                        f.write(f"{msg['role']}: {msg['content']}\n")
                history_win.addstr("История сохранена в chat_history.txt.\n", GREEN)
            elif user_input.lower() in ("exit", "quit"):
                history_win.addstr("До свидания!\n", GREEN)
                history_win.refresh()
                break
            elif user_input:
                messages.append({"role": "user", "content": user_input})
                assistant_reply = stream_response(api_key, messages, history_win)
                if assistant_reply:
                    messages.append({"role": "assistant", "content": assistant_reply})
                    tokens_used = count_tokens(assistant_reply)
                    history_win.addstr(f"Токенов использовано: {tokens_used}\n", YELLOW)

            history_win.refresh()

        except Exception as e:
            history_win.addstr(f"Ошибка: {str(e)}\n", RED)
            history_win.refresh()
            stdscr.getch()
            break

def main():
    try:
        curses.wrapper(chat_interface)
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()