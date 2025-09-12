from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Delete_order
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import Order
from sqlalchemy import select, delete

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Delete_order.id, F.text)
async def delete_order(message:Message,state:FSMContext):
    session=session_maker()
    order=await session.scalar(select(Order).where(Order.id==message.text.lower()))
    await session.close()
    if order is None:
        await message.answer(f'Нет такого заказа',reply_markup=template('Отменить',placeholder='Укажите ID заказа',size=(1,)))
        return
    await state.update_data(id=message.text.lower())
    await state.set_state(Delete_order.finish)
    await message.answer(f'Удалить заказ: {message.text.lower()}',reply_markup=template('Удалить','Назад','Отменить',
            placeholder='Выберите опцию',size=(3,)))
    await message.delete()
        
@router.message(Delete_order.id)
async def delete_order(message:Message):
    await message.answer(f'Введено неверное значение',reply_markup=template('Отменить',placeholder='Укажите ID заказа',size=(1,)))
    await message.delete()
        
@router.message(Delete_order.finish, F.text.lower()=='удалить')
async def delete_order(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    await session.execute(delete(Order).where(Order.id==data['id']))
    await session.commit()
    await session.close()
    await message.answer(f'Готово',reply_markup=template('Разместить','Изменить','Удалить',placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(Delete_order.finish, F.text.lower()=='назад')
async def delete_order(message:Message,state:FSMContext):
    await state.set_state(Delete_order.id)
    await message.answer(f'Укажите ID заказа',reply_markup=template('Отменить',placeholder='Укажите ID заказа',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Delete_order.finish))
async def delete_order(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Удалить товар: {data['id']}',reply_markup=template('Удалить','Назад','Отменить',placeholder='Выберите опцию',size=(1,2)))
    await message.delete()