from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, or_f
from filters.chat_filters import ChatFilter, AdminFilter
from keyboard.keyboard import template
from fsm.fsm import Post,Update,Delete,Post_category,Post_item,Post_cafe,Post_locale,Delete_locale
from fsm.fsm import Update_category,Update_item,Update_cafe,Delete_category,Delete_item,Delete_cafe,Delete_order
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

router=Router()
router.message.filter(ChatFilter(['private']),AdminFilter())

@router.message(StateFilter('*'),or_f(Command('admin'),F.text.lower()=='admin',F.text.lower()=='отменить'))
async def adm(message:Message,state:FSMContext):
    await message.answer(f'Привет, <b>{message.from_user.first_name}</b>',reply_markup=template('Разместить','Изменить','Удалить',
    		placeholder='Выберите опцию', size=(3,)))
    await message.delete()
    status=await state.get_state()
    if status is None:
        return
    await state.clear()
    
@router.message(StateFilter(None), or_f(F.text.lower()=='разместить', F.text.lower()=='изменить', F.text.lower()=='удалить'))
async def start_posting(message:Message,state:FSMContext):
    text=message.text.lower()
    if text=='разместить':
        await state.set_state(Post.option)
        await message.answer('Выберите опцию',reply_markup=template('Категория','Товар','Кафе','Локация','Отменить',
        	placeholder='Выберите опцию',size=(2,2,1)))
    elif text=='изменить':
        await message.answer('Выберите опцию',reply_markup=template('Категория','Товар','Кафе','Отменить',placeholder='Выберите опцию',size=(3,1)))
        await state.set_state(Update.option)
    elif text=='удалить':
        await state.set_state(Delete.option)
        await message.answer('Выберите опцию',reply_markup=template('Категория','Товар','Кафе','Локация','Заказ','Отменить',
        	placeholder='Выберите опцию',size=(2,3,1)))
    await message.delete()

@router.message(Post.option,F.text.lower()=='категория')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Post_category.belong)
    await message.answer('Выберите тип',reply_markup=template('Еда','Напитки','Назад','Отменить',placeholder='Выберите опцию',size=(2,2)))
    await message.delete()
    
@router.message(Post.option,F.text.lower()=='товар')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Post_item.category)
    await message.answer('Укажите категорию',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()
    
@router.message(Post.option,F.text.lower()=='кафе')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Post_cafe.cafe)
    await message.answer('Задайте адрес в следующем порядке: <b><i>Страна, Город, Улица, дом</i></b>',reply_markup=template('Отменить',
    		placeholder='Задайте адрес',size=(1,)))
    await message.delete()
    
@router.message(Post.option,F.text.lower()=='локация')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Post_locale.locale)
    await message.answer('Задайте локацию в следующем порядке: <b><i>Страна, Город</i></b>',reply_markup=template('Отменить',
            placeholder='Задайте локацию',size=(1,)))
    await message.delete()
    
@router.message(Update.option,F.text.lower()=='категория')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Update_category.title)
    await message.answer('Укажите категорию',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()
    
@router.message(Update.option,F.text.lower()=='товар')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Update_item.category)
    await message.answer('Укажите категорию',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()
    
@router.message(Update.option,F.text.lower()=='кафе')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Update_cafe.cafe)
    await message.answer('Задайте адрес в следующем порядке: <b><i>Страна, Город, Улица, дом</i></b>',reply_markup=template('Отменить',
            placeholder='Задайте адрес',size=(1,)))
    await message.delete()
    
@router.message(Delete.option,F.text.lower()=='категория')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Delete_category.title)
    await message.answer('Укажите категорию',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()
    
@router.message(Delete.option,F.text.lower()=='товар')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Delete_item.category)
    await message.answer('Укажите категорию',reply_markup=template('Отменить',placeholder='Укажите категорию',size=(1,)))
    await message.delete()
    
@router.message(Delete.option,F.text.lower()=='кафе')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Delete_cafe.cafe)
    await message.answer('Задайте адрес в следующем порядке: <b><i>Страна, Город, Улица, дом</i></b>',reply_markup=template('Отменить',
            placeholder='Задайте адрес',size=(1,)))
    await message.delete()
    
@router.message(Delete.option,F.text.lower()=='локация')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Delete_locale.locale)
    await message.answer('Задайте локацию в следующем порядке: <b><i>Страна, Город</i></b>',reply_markup=template('Отменить',
            placeholder='Задайте локацию',size=(1,)))
    await message.delete()
    
@router.message(Delete.option,F.text.lower()=='заказ')
async def select_option(message:Message,state:FSMContext):
    await state.set_state(Delete_order.id)
    await message.answer('Укажите ID заказа',reply_markup=template('Отменить',placeholder='Укажите ID заказа',size=(1,)))
    await message.delete()
        
@router.message(or_f(StateFilter(Post.option),StateFilter(Update.option),StateFilter(Delete.option)))
async def select_option(message:Message):
    await message.answer('Введено неверное значение',reply_markup=template('Категория','Товар','Кафе','Локация','Заказ','Отменить',
        	placeholder='Выберите опцию',size=(3,3)))
    await message.delete()