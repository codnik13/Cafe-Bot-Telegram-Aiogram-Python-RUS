from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Update_category
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import Category
from sqlalchemy import select, update

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Update_category.title, F.text)
async def spcify_name(message:Message,state:FSMContext):
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==message.text.lower()))
    await session.close()
    if category is None:
        await message.answer('Нет такой категории',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
        return
    await state.update_data(title=message.text.lower())
    await state.set_state(Update_category.prop)
    await message.answer('Укажите свойство',reply_markup=template('Назад','Отменить',placeholder='Укажите свойство',size=(2,)))
    await message.delete()
    
@router.message(Update_category.title)
async def name_check(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()
    
@router.message(Update_category.prop, F.text.lower()=='back')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_category.title)
    await message.answer('Укажите категорию',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()
    
@router.message(Update_category.prop, F.text)
async def specify_prop(message:Message,state:FSMContext):
    columns=Category.__table__.columns.keys()
    if message.text.lower() not in columns:
        await message.answer('Нет такого свойства',reply_markup=template('Назад','Отменить',placeholder='Укажите свойство',size=(2,)))
        return
    await state.update_data(prop=message.text.lower())
    await state.set_state(Update_category.value)
    await message.answer('Задайте новое значение',reply_markup=template('Назад','Отменить',placeholder='Задайте значение',size=(2,)))
    await message.delete()
    
@router.message(Update_category.prop)
async def prop_check(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить',placeholder='Задайте значение',size=(2,)))
    await message.delete()
    
@router.message(Update_category.value, F.text.lower()=='назад')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_category.prop)
    await message.answer('Укажите свойство',reply_markup=template('Назад','Отменить',placeholder='Укажите свойство',size=(2,)))
    await message.delete()
    
@router.message(Update_category.value, F.photo)
async def set_value(message:Message,state:FSMContext):
    data=await state.get_data()
    if data['prop']!='image':
        await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить',placeholder='Загрузите изображение',size=(2,)))
        return
    await state.update_data(value=message.photo[-1].file_id)
    await message.answer(f'Вы уверены?:',reply_markup=template('Изменить','Назад','Отменить',placeholder='Выберите опцию',size=(1,2)))
    await state.set_state(Update_category.finish)
    await message.delete()
    
@router.message(Update_category.value, F.text)
async def set_value(message:Message,state:FSMContext):
    data=await state.get_data()
    if data['prop']=='image':
        await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить',placeholder='Задайте значение',size=(2,)))
        return
    await state.update_data(value=message.text.lower())
    await message.answer(f'Изменить: {data['prop']} = {message.text.lower()}',reply_markup=template('Изменить','Назад','Отменить',
            placeholder='Выберите опцию',size=(2,1)))
    await state.set_state(Update_category.finish)
    await message.delete()
    
@router.message(Update_category.value)
async def value_check(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить',placeholder='Задайте значение',size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Update_category.finish), F.text.lower()=='изменить')
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    if data['prop']=='title':
        await session.execute(update(Category).where(Category.title==data['title']).values(title=data['value']))
    elif data['prop']=='image':
        await session.execute(update(Category).where(Category.title==data['title']).values(image=data['value']))
    await session.commit()
    await session.close()
    await message.answer(f'Done',reply_markup=template('Разместить','Изменить','Удалить',placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(Update_category.finish, F.text.lower()=='назад')
async def update_cafe(message:Message,state:FSMContext):
    await state.set_state(Update_category.value)
    await message.answer('Задайте новое значение',reply_markup=template('Назад','Отменить',placeholder='Задайте значение',size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Update_category.finish))
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Изменить: {data['prop']} = {data['value']}',reply_markup=template('Изменить','Назад','Отменить',
            placeholder='Выберите опцию', size=(2,1)))
    await message.delete()