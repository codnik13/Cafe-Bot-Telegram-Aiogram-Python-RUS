from aiogram import Router, F
from aiogram.types import Message
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Update_cafe
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.engine import session_maker
from database.models import Cafe
from sqlalchemy import select, update

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Update_cafe.cafe, F.text)
async def update_cafe(message:Message,state:FSMContext):
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
    await state.set_state(Update_cafe.prop)
    await message.answer('Укажите свойство',reply_markup=template('Назад','Отменить',placeholder='Укажите свойство',size=(2,)))
    await message.delete()
    
@router.message(Update_cafe.cafe)
async def update_cafe(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Отменить',placeholder='Укажите адрес кафе',size=(1,)))
    await message.delete()
    
@router.message(Update_cafe.prop, F.text.lower()=='назад')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_cafe.cafe)
    await message.answer('Укажите адрес в следующем порядке: <b><i>Страна, Город, Улица, дом</i></b>',reply_markup=template('Отменить',
        	placeholder='Укажите адрес кафе',size=(1,)))
    await message.delete()
    
@router.message(Update_cafe.prop, F.text)
async def update_cafe(message:Message,state:FSMContext):
    columns=Cafe.__table__.columns.keys()
    if message.text.lower() not in columns:
        await message.answer('Нет такого свойства',reply_markup=template('Назад','Отменить',placeholder='Укажите свойство',size=(2,)))
        return
    await message.answer('Задайте новое значение',reply_markup=template('Назад','Отменить',placeholder='Задайе новое значение',size=(2,)))
    await state.update_data(prop=message.text.lower())
    await state.set_state(Update_cafe.value)
    await message.delete()
    
@router.message(Update_cafe.prop)
async def update_cafe(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить', placeholder='Укажите свойство', size=(2,)))
    await message.delete()
    
@router.message(Update_cafe.value, F.text.lower()=='назад')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_cafe.prop)
    await message.answer('Укажите свойство',reply_markup=template('Назад','Отменить',placeholder='Укажите свойство',size=(2,)))
    await message.delete()
    
@router.message(Update_cafe.value, F.text)
async def update_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.update_data(value=message.text.lower())
    await message.answer(f'Изменить: {data['prop']} = {message.text.lower()}',reply_markup=template('Изменить','Назад','Отменить',
            placeholder='Выберите опцию',size=(2,1)))
    await state.set_state(Update_cafe.finish)
    await message.delete()
    
@router.message(Update_cafe.value)
async def update_cafe(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить', placeholder='Укажите новое значение',size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Update_cafe.finish), F.text.lower()=='изменить')
async def update_cafe(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    text=(data['cafe']).split(', ')
    session=session_maker()
    if data['prop']=='country':
        await session.execute(update(Cafe)
            .where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]).values(country=data['value']))
    elif data['prop']=='town':
        await session.execute(update(Cafe)
            .where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]).values(town=data['value']))
    elif data['prop']=='street':
        await session.execute(update(Cafe)
            .where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]).values(street=data['value']))
    elif data['prop']=='house':
        await session.execute(update(Cafe)
            .where(Cafe.country==text[0],Cafe.town==text[1],Cafe.street==text[2],Cafe.house==text[3]).values(house=data['value']))
    await session.commit()
    await session.close()
    await message.answer(f'Готово',reply_markup=template('Разместить','Изменить','Удалить',placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(Update_cafe.finish, F.text.lower()=='назад')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_cafe.value)
    await message.answer('Задайте новое значение',reply_markup=template('Назад','Отменить',placeholder='Задайте новое значение',size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Update_cafe.finish))
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Изменить: {data['prop']} = {data['value']}',reply_markup=template('Изменить','Назад','Отменить',
            placeholder='Выберите опцию',size=(2,1)))
    await message.delete()