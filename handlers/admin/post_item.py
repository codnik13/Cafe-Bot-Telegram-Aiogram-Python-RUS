from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Post_item
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import Item, Category
from sqlalchemy import select

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())
    
@router.message(Post_item.category, F.text)
async def post_item(message:Message,state:FSMContext):
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==message.text.lower()))
    await session.close()
    if category is None:
        await message.answer('Нет такой категории',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
        return
    await state.update_data(category=message.text.lower())
    await state.set_state(Post_item.name)
    await message.answer('Задайте название товара',reply_markup=template('Назад','Отменить',placeholder='Задайте название товара',size=(2,)))
    await message.delete()
    
@router.message(Post_item.category)
async def post_item(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()
    
@router.message(Post_item.name, F.text.lower()=='назад')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_item.category)
    await message.answer('Укажите категорию',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()

@router.message(Post_item.name, F.text)
async def post_item(message:Message,state:FSMContext):
    data=await state.get_data()
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==data['category']))
    item=await session.scalar(select(Item).where(Item.category==category.id,Item.name==message.text.lower()))
    await session.close()
    if item is not None:
        await message.answer('Товар уже существует',reply_markup=template('Назад','Отменить',placeholder='Задайте название товара',size=(2,)))
        return
    await state.update_data(name=message.text.lower())
    await state.set_state(Post_item.details)
    await message.answer('Задайте описание',reply_markup=template('Назад','Отменить',placeholder='Задайте описание',size=(2,)))
    await message.delete()
    
@router.message(Post_item.name)
async def post_item(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить',placeholder='Задайте название товара',size=(2,)))
    await message.delete()
    
@router.message(Post_item.details, F.text.lower()=='назад')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_item.name)
    await message.answer('Задайте название товара',reply_markup=template('Назад','Отменить',placeholder='Задайте название товара',size=(2,)))
    await message.delete()
    
@router.message(Post_item.details, F.text)
async def post_item(message:Message,state:FSMContext):
    await state.update_data(details=message.text.lower())
    await state.set_state(Post_item.image)
    await message.answer('Загрузите изображение',reply_markup=template('Назад','Отменить',placeholder='Загрузите озображение',size=(2,)))
    await message.delete()
    
@router.message(Post_item.details)
async def post_item(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить',placeholder='Задайте описание',size=(2,)))
    await message.delete()
    
@router.message(Post_item.image, F.photo)
async def post_item(message:Message,state:FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(Post_item.price)
    await message.answer('Установите цену',reply_markup=template('Назад','Отменить',placeholder='Установите цену',size=(2,)))
    await message.delete()
    
@router.message(Post_item.image, F.text.lower()=='назад')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_item.details)
    await message.answer('Задайте описание',reply_markup=template('Назад','Отменить',placeholder='Задайте описание',size=(2,)))
    await message.delete()
    
@router.message(Post_item.image)
async def set_image(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить',placeholder='Загрузите изображение',size=(2,)))
    await message.delete()
    
@router.message(Post_item.price, F.text.lower()=='назад')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_item.image)
    await message.answer('Загрузите изображение',reply_markup=template('Назад','Отменить',placeholder='Загрузите изображение',size=(2,)))
    await message.delete()
    
@router.message(Post_item.price, F.text)
async def set_price(message:Message,state:FSMContext):
    await state.update_data(price=message.text.lower())
    data=await state.get_data()
    await state.set_state(Post_item.finish)
    await message.answer(f'Разместить: {data['name']} в категории {data['category']}, {data['details']}, цена: {message.text.lower()}',
        reply_markup=template('Разместить','Назад','Отменить',placeholder='Выберите опцию',size=(2,1)))
    await message.delete()
    
@router.message(Post_item.price)
async def set_price(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить',placeholder='Установите цену',size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Post_item.finish), F.text.lower()=='разместить')
async def post_item(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==data['category']))
    session.add(Item(name=data['name'],details=data['details'],image=data['image'],price=float(data['price']),category=category.id))
    await session.commit()
    await session.close()
    await message.answer(f'Готово',reply_markup=template('Разместить','Изменить','Удалить',placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(Post_item.finish, F.text.lower()=='назад')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_item.price)
    await message.answer('Установите цену',reply_markup=template('Назад','Отменить',placeholder='Установите цену',size=(2,)))
    await message.delete()
    
@router.message(StateFilter(Post_item.finish))
async def post_item(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Разместить: {data['name']} in category {data['category']}, {data['details']}, price: {data['price']}',
        reply_markup=template('Разместить','Назад','Отменить',placeholder='Выберите опцию',size=(2,1)))
    await message.delete()