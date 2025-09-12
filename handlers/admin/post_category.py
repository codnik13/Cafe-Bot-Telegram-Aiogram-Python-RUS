from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import StateFilter, or_f
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Post_category, Post
from aiogram.fsm.context import FSMContext
from database.engine import session_maker
from database.models import Category
from sqlalchemy import select

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())

@router.message(Post_category.belong,or_f(F.text.lower()=='еда',F.text.lower()=='напитки'))
async def post_category(message:Message,state:FSMContext):
    await state.update_data(belong=message.text.lower())
    await message.answer(f'Задайте категорию',reply_markup=template('Назад','Отменить',placeholder='Задайте категорию',size=(2,)))
    await state.set_state(Post_category.title)
    await message.delete()

@router.message(Post_category.belong, F.text.lower()=='назад')
async def post_category(message:Message,state:FSMContext):
    await state.set_state(Post.option)
    await message.answer('Выберите опцию',reply_markup=template('Категория','Товар','Кафе','Локация','Отменить',placeholder='Выберите опцию',size=(2,2,1)))
    await message.delete()
    
@router.message(Post_category.belong)
@router.message(Post_category.title, F.text.lower()=='назад')
async def post_category(message:Message,state:FSMContext):
    await state.set_state(Post_category.belong)
    await message.answer(f'Выберите тип',reply_markup=template('Еда','Напитки','Отменить',placeholder='Выберите тип',size=(2,1)))
    await message.delete()

@router.message(Post_category.title, F.text)
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    session=session_maker()
    category=await session.scalar(select(Category).where(Category.title==message.text.lower(),Category.belong==data['belong']))
    await session.close()
    if category is not None:
        await message.answer('Категория уже существует',reply_markup=template('Назад','Отменить',placeholder='Задайте категорию',size=(2,)))
        return
    await state.update_data(title=message.text.lower())
    data=await state.get_data()
    await message.answer(f'Загрузите изображение',reply_markup=template('Назад','Отменить',placeholder='Загрузите изображение',size=(2,)))
    await state.set_state(Post_category.image)
    await message.delete()
    
@router.message(Post_category.title)
async def post_category(message:Message):
    await message.answer('Задайте категорию',reply_markup=template('Отменить',placeholder='Задайте категорию',size=(1,)))
    await message.delete()
    
@router.message(Post_category.image, F.photo)
async def post_item(message:Message,state:FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.set_state(Post_category.finish)
    data=await state.get_data()
    await message.answer(f'Разместить: {data['title']}, {data['belong']}',reply_markup=template('Разместить','Назад','Отменить',
            placeholder='Выберите опцию',size=(1,2)))
    await message.delete()
    
@router.message(Post_category.image, F.text.lower()=='назад')
async def post_item(message:Message,state:FSMContext):
    await state.set_state(Post_category.title)
    await message.answer('Задайте категорию',reply_markup=template('Назад','Отменить',placeholder='Задайте категорию',size=(2,)))
    await message.delete()
    
@router.message(Post_category.image)
async def set_image(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Назад','Отменить',placeholder='Загрузите изображение',size=(2,)))
    await message.delete()

@router.message(StateFilter(Post_category.finish), F.text.lower()=='разместить')
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await state.clear()
    session=session_maker()
    session.add(Category(title=data['title'],belong=data['belong'],image=data['image']))
    await session.commit()
    await session.close()
    await message.answer(f'Готово',reply_markup=template('Разместить','Изменить','Удалить',placeholder='Выберите опцию',size=(3,)))
    await message.delete()
    
@router.message(StateFilter(Post_category.finish),F.text.lower()=='назад')
async def post_category(message:Message,state:FSMContext):
    await state.set_state(Post_category.title)
    await message.answer('Задайте категорию',reply_markup=template('Отменить',placeholder='Задайте категорию',size=(1,)))
    await message.delete()
    
@router.message(StateFilter(Post_category.finish))
async def post_category(message:Message,state:FSMContext):
    data=await state.get_data()
    await message.answer(f'Разместить: {data['title']}, {data['belong']}',reply_markup=template('Разместить','Назад','Отменить',
            placeholder='Выберите опцию',size=(2,1)))
    await message.delete()