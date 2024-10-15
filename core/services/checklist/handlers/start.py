from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import config
from core.database.checklist_query import CheckListQuery
from core.database.enums.checklists import EnumCheckListContentActions
from core.database.model import ClientRolesEnum, ChecklistContent
from core.database.query import Database
from core.loggers.bot_logger import Logger
from ..callback_data import CLMenu, CLContent
from ..keyboards import inline
from core.utils import texts
from core.services.checklist.pd_models.pd_start import PDCLContent, PDCheckList, Answer, Content
from ..states import StatesCheckList


async def send_next_page(nextclcontent: ChecklistContent | None, message: Message, state: FSMContext):
    if nextclcontent is None:
        data = await state.get_data()
        complete_checklist = PDCheckList.model_validate_json(data['complete_checklist'])
        text = (f'{texts.information_head}'
                f'Чек-лист "<b>{complete_checklist.menu_name}</b>" успешно пройден\n'
                f'<b>Завершите</b> чек-лист')
        await message.answer(text, reply_markup=inline.kb_end_content())
    elif nextclcontent.action.action == EnumCheckListContentActions.NONE:
        if nextclcontent.file_id is not None:
            await message.bot.send_photo(
                message.chat.id,
                nextclcontent.file_id,
                caption=nextclcontent.content,
                reply_markup=inline.kb_end_content())
        else:
            await message.answer(
                nextclcontent.content,
                reply_markup=inline.kb_content(nextclcontent)
            )
        await state.set_state(StatesCheckList.NONE)
    elif nextclcontent.action.action == EnumCheckListContentActions.GET_TEXT:
        if nextclcontent.file_id is not None:
            await message.bot.send_photo(
                message.chat.id,
                nextclcontent.file_id,
                caption=nextclcontent.content,
            )
        else:
            await message.answer(nextclcontent.content)
        await state.set_state(StatesCheckList.GET_TEXT)
    elif nextclcontent.action.action == EnumCheckListContentActions.GET_PHOTO:
        if nextclcontent.file_id is not None:
            await message.bot.send_photo(
                message.chat.id,
                nextclcontent.file_id,
                caption=nextclcontent.content,
            )
        else:
            await message.answer(nextclcontent.content)
        await state.set_state(StatesCheckList.GET_PHOTO)


router = Router()
cl_query = CheckListQuery()


@router.message(Command("checklist"))
async def start(message: Message, state: FSMContext, log: Logger, db: Database):
    log.button('/checklist')
    await state.clear()

    # Если включен режим разработчика
    if not config.bot_cfg.develope_mode:
        await message.answer(texts.is_develope)
        return

    client = await db.get_client(message.from_user.id)
    if client.role.rolename in [ClientRolesEnum.ADMIN, ClientRolesEnum.SUPERADMIN]:
        await message.answer("Выберите нужную операцию",
                             reply_markup=inline.kb_admins_panel())
    else:
        menus = await cl_query.get_all_checklist_menus()
        if not menus:
            await message.answer(f"{texts.error_head}"
                                 f"Нет созданных меню\n"
                                 f"Обратитесь к Администратору для создания меню")
            log.error(f"Нет созданных меню")
            return
        await message.answer("Выберите нужную операцию",
                             reply_markup=inline.kb_checklist(menus))


@router.callback_query(F.data == 'list_checklists')
async def list_checklists(call: CallbackQuery, log: Logger):
    log.button('Список Чек-листов')
    menus = await cl_query.get_all_checklist_menus()
    if not menus:
        await call.message.edit_text(
            f"{texts.error_head}"
            f"Нет созданных меню\n"
            f"Обратитесь к Администратору для создания меню")
        log.error(f"Нет созданных меню")
        return
    await call.message.edit_text("Выберите нужную операцию",
                                 reply_markup=inline.kb_checklist(menus))


@router.callback_query(CLMenu.filter())
async def checklist_menu(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: CLMenu):
    menu = await cl_query.get_checklist_menu(callback_data.id)
    log.info(f'Выбрали чек-лист меню "{menu.name}"')
    clcontent = await cl_query.checlist_content_by_page(menu.id)
    if not clcontent:
        await call.message.answer(f"{texts.error_head}"
                                  f"Нет созданных чек-листов\n"
                                  f"Обратитесь к Администратору для создания чек-листа")
        log.error(f"Нет созданных чек-листов")
        return

    content = Content(
        id=clcontent.id,
        content=clcontent.content,
        file_id=clcontent.file_id,
        page=clcontent.page,
        checklistmenuid=clcontent.checklistmenuid
    )
    await state.update_data(
        current_checklist_content=content.model_dump_json(),
    )
    await send_next_page(
        nextclcontent=clcontent,
        message=call.message,
        state=state
    )


@router.callback_query(CLContent.filter(), StatesCheckList.NONE)
async def checklist_none(call: CallbackQuery, state: FSMContext, log: Logger, callback_data: CLContent):
    data = await state.get_data()
    clcontent = await cl_query.checlist_content_by_page(callback_data.menu_id, callback_data.page)
    log.info(f'Чек-лист "{clcontent.menu.name}" подтвердил страницу "{callback_data.page}"')
    content = Content(
        id=clcontent.id,
        content=clcontent.content,
        file_id=clcontent.file_id,
        page=clcontent.page,
        checklistmenuid=clcontent.checklistmenuid
    )
    answer = Answer(
        content=content,
        action=clcontent.action.action,
    )

    if data.get('complete_checklist') is not None:
        complete_checklist = PDCheckList.model_validate_json(data['complete_checklist'])
        complete_checklist.answers.append(answer)
    else:
        complete_checklist = PDCheckList(
            answers=[answer],
            menu_name=clcontent.menu.name,
        )

    await state.update_data(
        complete_checklist=complete_checklist.model_dump_json(),
    )

    nextclcontent = await cl_query.checlist_content_by_page(clcontent.checklistmenuid, page=clcontent.page + 1)
    await send_next_page(
        nextclcontent=nextclcontent,
        message=call.message,
        state=state
    )

    if nextclcontent is not None:
        await state.update_data(
            last_checklist_content=Content(
                id=nextclcontent.id,
                content=nextclcontent.content,
                file_id=nextclcontent.file_id,
                page=nextclcontent.page,
                checklistmenuid=nextclcontent.checklistmenuid
            ).model_dump_json()
        )


@router.message(StatesCheckList.GET_TEXT)
async def checklist_get_text(message: Message, state: FSMContext, log: Logger):
    data = await state.get_data()
    content = Content.model_validate_json(data.get('last_checklist_content'))
    clcontent = await cl_query.get_checklist_content(content.id)
    log.info(f'Чек-лист "{clcontent.menu.name}" ответил "{message.text}" страницу "{content.page}"')
    answer = Answer(
        content=Content(
            id=clcontent.id,
            content=clcontent.content,
            file_id=clcontent.file_id,
            page=clcontent.page,
            checklistmenuid=clcontent.checklistmenuid
        ),
        action=clcontent.action.action,
        text=message.text,
    )

    if data.get('complete_checklist') is not None:
        complete_checklist = PDCheckList.model_validate_json(data['complete_checklist'])
        complete_checklist.answers.append(answer)
    else:
        complete_checklist = PDCheckList(
            answers=[answer],
            menu_name=clcontent.menu.name,
        )

    await state.update_data(
        complete_checklist=complete_checklist.model_dump_json(),
    )

    nextclcontent = await cl_query.checlist_content_by_page(clcontent.checklistmenuid, page=clcontent.page + 1)
    await send_next_page(
        nextclcontent=nextclcontent,
        message=message,
        state=state
    )

    if nextclcontent is not None:
        await state.update_data(
            last_checklist_content=Content(
                id=nextclcontent.id,
                content=nextclcontent.content,
                file_id=nextclcontent.file_id,
                page=nextclcontent.page,
                checklistmenuid=nextclcontent.checklistmenuid
            ).model_dump_json()
        )


@router.message(StatesCheckList.GET_PHOTO, F.content_type.in_([ContentType.PHOTO]))
async def checklist_get_photo(message: Message, state: FSMContext, log: Logger):
    data = await state.get_data()
    last_content = Content.model_validate_json(data.get('last_checklist_content'))
    clcontent = await cl_query.get_checklist_content(last_content.id)
    log.info(f'Чек-лист "{clcontent.menu.name}" прислал фото "{message.photo[0].file_id}" страницу "{clcontent.page}"')
    answer = Answer(
        content=Content(
            id=clcontent.id,
            content=clcontent.content,
            file_id=clcontent.file_id,
            page=clcontent.page,
            checklistmenuid=clcontent.checklistmenuid
        ),
        action=clcontent.action.action,
        file_id=message.photo[0].file_id,
        text=message.caption,
    )

    if data.get('complete_checklist') is not None:
        complete_checklist = PDCheckList.model_validate_json(data['complete_checklist'])
        complete_checklist.answers.append(answer)
    else:
        complete_checklist = PDCheckList(
            answers=[answer],
            menu_name=clcontent.menu.name,
        )
    await state.update_data(
        complete_checklist=complete_checklist.model_dump_json(),
    )

    nextclcontent = await cl_query.checlist_content_by_page(clcontent.checklistmenuid, page=clcontent.page + 1)
    await send_next_page(
        nextclcontent=nextclcontent,
        message=message,
        state=state
    )

    if nextclcontent is not None:
        await state.update_data(
            last_checklist_content=Content(
                id=nextclcontent.id,
                content=nextclcontent.content,
                file_id=nextclcontent.file_id,
                page=nextclcontent.page,
                checklistmenuid=nextclcontent.checklistmenuid
            ).model_dump_json()
        )


@router.callback_query(F.data == 'checklist_content_end')
async def checklist_content_end(call: CallbackQuery, state: FSMContext, log: Logger):
    data = await state.get_data()
    if data.get('complete_checklist') is None:
        await call.message.edit_text(texts.error_head + "Что-то пошло не так,попробуйте еще раз пройти чек-лист")
        await log.error(f'Не смогли завершить чек-лист')
        return
    complete_checklist = PDCheckList.model_validate_json(data.get('complete_checklist'))
    await cl_query.complete_checklist(complete_checklist, call.from_user.id)
    log.success(f'Завершили чек-лист "{complete_checklist.menu_name}"')
    await call.message.edit_text(texts.success_head + f'Чек-лист "{complete_checklist.menu_name}" завершен')
    await state.clear()
