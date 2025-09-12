from aiogram import Router, F
from aiogram.types import Message
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Post_cafe
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.engine import session_maker
from database.models import Cafe
from sqlalchemy import select

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Post_cafe.cafe, F.text)
async def post_cafe(message:Message,state:FSMContext):
    text=message.text.lower().split(', ')
    if len(text)!=4:
        await message.answer('Введено неверное значение',reply_markup=template('Отменить',placeholder='Задайте адрес кафе',size=(1,)))
        return
    session=session_maker()
    cafe=await session.scalar(select(Cafe).where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]))
    await session.close()
    if cafe is not None:
        await message.answer('Такой адрес уже существует',reply_markup=template('Назад','Отменить',placeholder='Задайте адрес кафе',size=(2,)))
        return
    await state.update_data(cafe=message.text.lower())
    await state.set_state(Post_cafe.finish)
    await message.answer(f'Разместить: {text[0]}, {text[1]}, {text[2]}, {text[3]}',reply_markup=template('Разместить','Назад','Отменить',
			placeholder='Выберите опцию',size=(2,1)))
    await message.delete()
    
@router.message(Post_cafe.cafe)
async def post_cafe(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Отменить',placeholder='Задайте адрес кафе',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Post_cafe.finish),F.text.lower()=='разместить')
async def post_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    text=(data['cafe']).split(', ')
    session=session_maker()
    session.add(Cafe(country=text[0],town=text[1],street=text[2],house=text[3]))
    await session.commit()
    await session.close()
    await message.answer(f'Готово',reply_markup=template('Разместить','Изменить','Удалить',placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(StateFilter(Post_cafe.finish),F.text.lower()=='назад')
async def post_cafe(message:Message,state:FSMContext):
    await state.set_state(Post_cafe.cafe)
    await message.answer('Задайте локацию в следующем порядке: <b><i>Страна, Город, Улица, дом</i></b>',
        	placeholder='Задайте адрес кафе',reply_markup=template('Отменить',size=(1,)))
    await message.delete()

@router.message(StateFilter(Post_cafe.finish))
async def post_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    text=(data['cafe']).split(', ')
    await message.answer(f'Разместить: {text[0]}, {text[1]}, {text[2]}, {text[3]}',reply_markup=template('Разместить','Назад','Отменить',
            placeholder='Выберите опцию',size=(2,1)))
    await message.delete()
