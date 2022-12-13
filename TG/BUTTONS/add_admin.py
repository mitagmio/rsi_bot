from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from database_connector import db_admin
from keyboards import Keyboards
from main import dp, bot
from states import RegisterNewAdmin, DeleteAdmin

kbd = Keyboards()
admins_kbd = kbd.admin_settings()


@dp.callback_query_handler(text='add_admin')
async def admin_settings(message: Message):
    """main btn what returns kbd w/ admin config"""
    mes_id = message['message']['message_id']
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=f'You are in stage to add/delete or get list of admins.',
        reply_markup=admins_kbd
    )


@dp.callback_query_handler(Text(startswith="admin_settings_"))
async def admin_handler(message: Message):
    """handles btns from main admin settings"""
    data = message.data.split('admin_settings_')[1]
    mes_id = message['message']['message_id']
    if data == 'add':
        await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=mes_id,
            text=f'Enter new admin user id from @getmyid_bot:'
        )
        await RegisterNewAdmin.admin_id.set()
    elif data == 'list':
        data = db_admin.get_admins_list()
        text = 'Admin list:\n'
        for admin_id in range(len(data)):
            text += f'<code>{data[admin_id][0]}</code>\n'
        await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=mes_id,
            text=text,
            reply_markup=admins_kbd
        )
    elif data == 'delete':
        await DeleteAdmin.admin_id.set()
        await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=mes_id,
            text='Enter admin id, what you want to delete: '
        )


@dp.message_handler(state=RegisterNewAdmin.admin_id)
async def add_admin(message: Message, state: FSMContext):
    """add new admin"""
    try:
        db_admin.add_admin(message.text)
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'You add admin <i>{message.text}</i>.',
            reply_markup=admins_kbd
        )
    except Exception as err:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'Error: {err}.',
            reply_markup=admins_kbd
        )
    await state.finish()


@dp.message_handler(state=DeleteAdmin.admin_id)
async def delete_admin(message: Message, state: FSMContext):
    """delete admin by his id"""
    try:
        db_admin.delete_admin(message.text)
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'You deleted admin <i>{message.text}</i>.',
            reply_markup=admins_kbd
        )
    except Exception as err:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'Error: {err}.',
            reply_markup=admins_kbd
        )
    await state.finish()
