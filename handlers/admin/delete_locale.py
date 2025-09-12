from aiogram import Router, F
from aiogram.types import Message
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Delete_locale
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.engine import session_maker
from database.models import Locale
from sqlalchemy import select, delete

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Delete_locale.locale, F.text)
async def delete_locale(message:Message,state:FSMContext):
    text=message.text.lower().split(', ')
    if len(text)!=2:
        await message.answer('Ввведено неверное значение',reply_markup=template('Отменить',placeholder='Укажите локацию',size=(1,)))
        return
    session=session_maker()
    locale=await session.scalar(select(Locale).where(Locale.country==text[0],Locale.town==text[1]))
    await session.close()
    if locale is None:
        await message.answer('Нет такой локации',reply_markup=template('Отменить',placeholder='Укажите локацию',size=(1,)))
        return
    await state.update_data(locale=message.text.lower())
    await state.set_state(Delete_locale.finish)
    await message.answer(f'Удалить локацию: {text[0]}, {text[1]}',reply_markup=template('Удалить','Назад','Отменить',
            placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(Delete_locale.locale)
async def delete_locale(message:Message):
    await message.answer('Ввведено неверное значение',reply_markup=template('Отменить',placeholder='Укажите локацию',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Delete_locale.finish),F.text.lower()=='удалить')
async def delete_locale(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    text=(data['locale']).split(', ')
    session=session_maker()
    await session.execute(delete(Locale).where(Locale.country==text[0],Locale.town==text[1]))
    await session.commit()
    await session.close()
    await message.answer(f'Готово',reply_markup=template('Разместить','Изменить','Удалить',placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(StateFilter(Delete_locale.finish),F.text.lower()=='назад')
async def delete_locale(message:Message,state:FSMContext):
    await state.set_state(Delete_locale.locale)
    await message.answer('Укажите локацию в следующем порядке: <b><i>Страна, Город</i></b>',reply_markup=template('Отменить',
            placeholder='Укажите локацию',size=(1,)))
    await message.delete()

@router.message(StateFilter(Delete_locale.finish))
async def delete_locale(message:Message,state:FSMContext):
    data=await state.get_data()
    text=(data['locale']).split(', ')
    await message.answer(f'Удалить: {text[0]}, {text[1]}',reply_markup=template('Удалить','Назад','Отменить',placeholder='Выберите опцию',size=(3,)))
    await message.delete()