from aiogram import Router, F
from aiogram.types import Message
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Delete_category
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from database.engine import session_maker
from database.models import Category
from sqlalchemy import select, delete

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Delete_category.title, F.text)
async def delete_category(message:Message,state:FSMContext):
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==message.text.lower()))
    await session.close()
    if category is None:
        await message.answer(f'Нет такой категории',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
        return
    await state.update_data(title=message.text.lower())
    await state.set_state(Delete_category.finish)
    await message.answer(f'Удалить категорию: {message.text.lower()}',reply_markup=template('Удалить','Назад','Отменить',
        	placeholder='Выберите опцию',size=(3,)))
    await message.delete()
        
@router.message(Delete_category.title)
async def delete_category(message:Message):
    await message.answer(f'Введено неверное значение',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()
        
@router.message(Delete_category.finish, F.text.lower()=='удалить')
async def delete_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    await session.execute(delete(Category).where(Category.title==data['title']))
    await session.commit()
    await session.close()
    await message.answer(f'Готово',reply_markup=template('Разместить','Изменить','Удалить',placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(Delete_category.finish, F.text.lower()=='назад')
async def delete_category(message:Message,state:FSMContext):
    await state.set_state(Delete_category.title)
    await message.answer(f'Укажите категорию',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Delete_category.finish))
async def delete_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Удалить категорию: {data['title']}',reply_markup=template('Удалить','Назад','Отменить',size=(1,2)))
    await message.delete()