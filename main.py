import subprocess
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# замените <YOUR_BOT_TOKEN> на токен вашего бота
bot = Bot(token='<YOUR_BOT_TOKEN>')
dp = Dispatcher(bot)

# ID администратора
ADMIN_ID = <YOUR_ADMIN_ID>

# логирование в файл
logging.basicConfig(filename='bot.log', level=logging.INFO)

# список выполненных команд
executed_commands = []

# функция для выполнения команд на сервере
async def run_command(command, sudo=False):
    # добавляем sudo если необходимо
    if sudo:
        command = 'sudo ' + command

    # используем модуль subprocess для выполнения команд в терминале
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    result = output.decode().strip()
    if error:
        result += "\n\nОшибка:\n" + error.decode()
    return result

# обработчик команды /exec
@dp.message_handler(commands=['exec'])
async def exec_command(message: types.Message):
    # проверяем, что запрос отправил администратор
    if message.from_user.id != ADMIN_ID:
        logging.warning(f"Пользователь {message.from_user.id} попытался выполнить команду {message.text}")
        return

    # получаем аргументы команды
    command = message.get_args()

    # проверяем, что команда не пустая
    if not command:
        await message.reply("Пожалуйста, укажите команду для выполнения.")
        return

    # выполняем команду и отправляем результат обратно ботом
    try:
        result = await run_command(command)
    except Exception as e:
        result = str(e)

    executed_commands.append({'user_id': message.from_user.id, 'command': command, 'result': result})

    await message.reply(result)

# обработчик команды /last
@dp.message_handler(commands=['last'])
async def last_command(message: types.Message):
    # проверяем, что запрос отправил администратор
    if message.from_user.id != ADMIN_ID:
        logging.warning(f"Пользователь {message.from_user.id} попытался выполнить команду {message.text}")
        return

    # получаем количество последних выполненных команд
    count = int(message.get_args()) if message.get_args().isdigit() else 10

    # выводим результаты последних выполненных команд
    result = ''
    for command in executed_commands[-count:]:
        result += f"ID пользователя: {command['user_id']}, команда: {command['command']}, результат: {command['result']}\n\n"
    await message.reply(result)

# обработчик команды /help
@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    # проверяем, что запрос отправил администратор
    if message.from_user.id != ADMIN_ID:
        logging.warning(f"Пользователь {message.from_user.id} попытался выполнить команду {message.text}")
        return

    # выводим список доступных команд
    result = "/exec команда - выполнить команду на сервере\n"
    result += "/last [количество] - показать последние выполненные команды (по умолчанию показываются последние 10)\n"
    result += "/test - отправить echo команду 'Hello world' и получить ответ\n"
    result += "/help - показать доступные команды"
    await message.reply(result)

# обработчик команды /test
@dp.message_handler(commands=['test'])
async def test_command(message: types.Message):
    # отправляем echo команду "Hello world" и получаем ответ
    result = await run_command('echo "Hello world"')

    await message.reply(result)

# обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # проверяем, что запрос отправил администратор
    if message.from_user.id != ADMIN_ID:
        return

    # отправляем приветственное сообщение и информацию о доступных командах
    await message.reply("Привет! Я бот для выполнения команд на сервере. Доступные команды:\n\n"
                        "/exec команда - выполнить команду на сервере\n"
                        "/last [количество] - показать последние выполненные команды (по умолчанию показываются последние 10)\n"
                        "/test - отправить echo команду 'Hello world' и получить ответ\n"
                        "/help - показать доступные команды")

# запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp)