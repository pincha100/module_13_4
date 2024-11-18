from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor


API_TOKEN = ''
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Определяем группу состояний для цепочки "Calories"
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()



@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот, помогающий твоему здоровью. Введите 'Calories', чтобы начать расчёт нормы калорий.")


# Начало цепочки вопросов: ввод возраста
@dp.message_handler(Text(equals="Calories", ignore_case=True))
async def set_age(message: types.Message):
    await message.answer("Введите свой возраст:")
    await UserState.age.set()


# Обработка возраста и переход к росту
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))  # Сохраняем возраст
    await message.answer("Введите свой рост (в сантиметрах):")
    await UserState.growth.set()


# Обработка роста и переход к весу
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))  # Сохраняем рост
    await message.answer("Введите свой вес (в килограммах):")
    await UserState.weight.set()


# Обработка веса и подсчёт нормы калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=int(message.text))  # Сохраняем вес

    # Получаем все данные пользователя
    data = await state.get_data()
    age = data["age"]
    growth = data["growth"]
    weight = data["weight"]

    # Формула Миффлина-Сан Жеора для мужчин:
    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    # Для женщин можно использовать: calories = 10 * weight + 6.25 * growth - 5 * age - 161

    # Отправляем результат пользователю
    await message.answer(f"Ваша норма калорий: {calories:.2f} ккал в день.")

    # Завершаем машину состояний
    await state.finish()


# Обработчик всех прочих сообщений
@dp.message_handler()
async def all_messages(message: types.Message):
    # Если сообщение не попало в другие обработчики
    await message.answer("Введите команду /start, чтобы начать общение.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
