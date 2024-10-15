from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.database.checklist_query import CheckListQuery
from core.loggers.bot_logger import Logger
from core.utils import texts
from ..callback_data import CLContentAction
from ..keyboards import inline
from ..pd_models.pd_admin import CLCreateMenu, CLCreateContent
from ..states import CreateChecklist

router = Router()
cl_query = CheckListQuery()


@router.callback_query(F.data == 'new_checklist')
async def new_checklists(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Добавить Чек-лист')
    await call.message.edit_text('Напишите название чек-листа')
    await state.set_state(CreateChecklist.name)


@router.message(CreateChecklist.name)
async def name_checklists(message: Message, state: FSMContext, log: Logger):
    log.info(f'Напечатал название чек-листа "{message.text}"')
    cl_menu = CLCreateMenu(name=message.text)
    await state.update_data(cl_menu=cl_menu.model_dump_json())
    await message.answer(f'Страница #️⃣{cl_menu.page}\n'
                         'Выберите действие от пользователя',
                         reply_markup=inline.kb_select_actions())
    await state.set_state(CreateChecklist.action)


@router.callback_query(CLContentAction.filter(), CreateChecklist.action)
async def select_action(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: CLContentAction):
    log.info(f'Выбрали действие "{callback_data.action}"')
    data = await state.get_data()
    cl_menu = CLCreateMenu.model_validate_json(data['cl_menu'])
    cl_create_content = CLCreateContent(
        action=callback_data.action,
        page=cl_menu.page,
    )
    await state.set_state(CreateChecklist.content)
    await state.update_data(cl_create_content=cl_create_content.model_dump_json())
    await call.message.edit_text(f'Страница #️⃣{cl_menu.page}\n'
                                 f'Напишите содержимое чек-листа, так же можете прикрепить 1 фото')


@router.message(CreateChecklist.content, F.content_type.in_([ContentType.PHOTO, ContentType.TEXT]))
async def content_checklists(message: Message, state: FSMContext, log: Logger):
    data = await state.get_data()
    if message.photo is not None:
        file_id = message.photo[-1].file_id
        text = message.caption
    elif message.document is not None:
        file_id = message.document.file_id
        text = message.caption
    else:
        file_id = None
        text = message.text

    cl_create_content = CLCreateContent.model_validate_json(data['cl_create_content'])
    cl_create_content.content = text
    cl_create_content.file_id = file_id

    cl_menu = CLCreateMenu.model_validate_json(data['cl_menu'])

    if file_id is not None:
        log.info(f'Напечатал содержимое чек-листа с фото "{text}"')
        await message.answer_photo(
            photo=file_id,
            caption=f'Страница #️⃣{cl_menu.page}\n{text}',
            reply_markup=inline.kb_confirm_new_content()
        )
    else:
        log.info(f'Напечатал содержимое чек-листа "{text}"')
        await message.answer(f'Страница #️⃣{cl_menu.page}\n{text}',
                             reply_markup=inline.kb_confirm_new_content())
    await state.update_data(
        cl_create_content=cl_create_content.model_dump_json()
    )


@router.callback_query(F.data == 'сhange_new_content')
async def change_new_content(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Изменить содержимое Чек-листа')
    await call.message.edit_text('Напишите содержимое чек-листа, так же можете прикрепить 1 фото')
    await state.set_state(CreateChecklist.content)


@router.callback_query(F.data == 'next_new_content')
async def next_new_content(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Следующая страница Чек-листа')
    data = await state.get_data()
    cl_create_content = CLCreateContent.model_validate_json(data['cl_create_content'])
    cl_menu = CLCreateMenu.model_validate_json(data['cl_menu'])
    cl_menu.page += 1
    cl_menu.contents.append(cl_create_content)
    await state.update_data(cl_menu=cl_menu.model_dump_json())
    await call.message.delete()
    await call.message.answer(f'Страница #️⃣{cl_menu.page}\n'
                              'Выберите действие от пользователя',
                              reply_markup=inline.kb_select_actions())
    await state.set_state(CreateChecklist.action)


@router.callback_query(F.data == 'confirm_new_content')
async def confirm_new_content(call: CallbackQuery, state: FSMContext, log: Logger):
    log.button('Завершить создание чек-листа')
    data = await state.get_data()
    cl_menu = CLCreateMenu.model_validate_json(data['cl_menu'])
    cl_create_content = CLCreateContent.model_validate_json(data['cl_create_content'])
    cl_menu.contents.append(cl_create_content)
    await cl_query.create_checklist(cl_menu)
    await call.message.delete()
    await call.message.answer(texts.success_head + f'Чек-лист "{cl_menu.name}" создан',
                              reply_markup=inline.kb_after_create_checklist())
    log.debug(cl_menu.model_dump_json())
    log.success(f'Чек-лист "{cl_menu.name}" создан')
    await state.clear()
