from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Delete_cafe
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import Cafe
from sqlalchemy import select, delete

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())

@router.message(Delete_cafe.cafe, F.text)
async def delete_cafe(message:Message,state:FSMContext):
    text=message.text.lower().split(', ')
    if len(text)!=4:
        await message.answer('Введено неверное значение',reply_markup=template('Отменить',placeholder='Укажите адрес кафе',size=(1,)))
        return
    session=session_maker()
    cafe=await session.scalar(select(Cafe).where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]))
    await session.close()
    if cafe is None:
        await message.answer('Нет такого кафе',reply_markup=template('Отменить',placeholder='Укажите адрес кафе',size=(1,)))
        return
    await state.update_data(cafe=message.text.lower())
    await state.set_state(Delete_cafe.finish)
    await message.answer(f'Удалить кафе: {text[0]}, {text[1]}, {text[2]}, {text[3]}',reply_markup=template('Удалить','Назад','Отменить',
            placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(Delete_cafe.cafe)
async def delete_cafe(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Отменить',placeholder='Укажите адрес кафе',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Delete_cafe.finish),F.text.lower()=='удалить')
async def delete_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    text=(data['cafe']).split(', ')
    session=session_maker()
    await session.execute(delete(Cafe).where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]))
    await session.commit()
    await session.close()
    await message.answer(f'Готово',reply_markup=template('Разместить','Изменить','Удалить',placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(StateFilter(Delete_cafe.finish),F.text.lower()=='назад')
async def delete_cafe(message:Message,state:FSMContext):
    await state.set_state(Delete_cafe.cafe)
    await message.answer('Укажите адрес в следующем порядке: <b><i>Страна, Город, Улица, дом</i></b>',reply_markup=template('Отменить',
            placeholder='Укажите адрес кафе',size=(1,)))
    await message.delete()

@router.message(StateFilter(Delete_cafe.finish))
async def delete_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    text=(data['cafe']).split(', ')
    await message.answer(f'Удалить кафе: {text[0]}, {text[1], text[2], text[3]}',reply_markup=template('Удалить','Назад','Отменить',
            placeholder='Выберите опцию',size=(3,)))
    await message.delete()