from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiohttp import ClientSession
import json


TG = ''  # токен тг бота из @BotFather
API_KEY = '' # апи от опенроутер


bot = Bot(token=TG)
dp = Dispatcher()

qwenurl = 'https://openrouter.ai/api/v1/chat/completions'
tgurl = 'https://api.telegram.org/file/bot'

async def zapros(messages):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': 'qwen/qwen2.5-vl-72b-instruct:free',
        'messages': messages,
    }
    async with ClientSession() as session:
        async with session.post(qwenurl, headers=headers, data=json.dumps(payload)) as response:
            if response.status == 200:
                result = await response.json()
                if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                    return result['choices'][0]['message']['content']
                else:
                    return "Ошибка, связанная с вашим апи"
            else:
                error_text = await response.text()
                return f'Ошибка: {response.status} - {error_text}'


@dp.message(F.text.lower() == '/start')
async def start_command(message: Message):
    await message.answer('<b>🚀 Напиши мне свой запрос, а я отвечу</b>\n'
                         '<i>Поддерживаются фото и текст</i>', parse_mode='HTML')

@dp.message(F.text)
async def handle_text(message: Message):
    messages = [{'role': 'user', 'content': [{'type': 'text', 'text': message.text}]}]
    response = await zapros(messages)
    await message.answer(response)


@dp.message(F.photo)
async def handle_photo(message: Message):
    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    photo_url = f'{tgurl}{TG}/{file_info.file_path}'

    messages = [
        {
            'role': 'user',
            'content': [
                {'type': 'image_url', 'image_url': {'url': photo_url}},
            ],
        }
    ]

    res = await zapros(messages)
    await message.answer(res)

async def zapusk():
    info = await bot.get_me()
    print(f'~~~ Бот @{info.username} запущен ~~~')
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(zapusk())
    except KeyboardInterrupt:
        print('~~~ Выключение бота ~~~')
