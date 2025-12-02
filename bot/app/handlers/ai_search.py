"""AI-powered search handlers."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from app.services.ai_assistant import AIAssistant
from app.keyboards.inline import build_paginated_keyboard, build_start_keyboard
from app.states.search import SearchStates
from app.constants import Messages

router = Router()
logger = logging.getLogger(__name__)


async def get_data_service(message_or_callback):
    """Get data service from bot context."""
    if hasattr(message_or_callback.bot, '_data_service'):
        return message_or_callback.bot._data_service
    return None


async def get_ai_assistant(message_or_callback):
    """Get AI assistant from bot context."""
    if hasattr(message_or_callback.bot, '_ai_assistant'):
        return message_or_callback.bot._ai_assistant
    return None


@router.callback_query(F.data == "ai_search")
async def start_ai_search(callback: CallbackQuery, state: FSMContext):
    """Start AI-powered search."""
    await state.set_state(SearchStates.ai_searching)
    await state.update_data(conversation_history=[])
    
    text = (
        "🤖 <b>ИИ Ассистент активирован!</b>\n\n"
        "Я помогу найти врача в Калуге. Напишите:\n"
        "• Какой врач нужен (специальность)\n"
        "• Где вы хотите его найти (адрес, район)\n\n"
        "<b>Примеры запросов:</b>\n"
        "• \"Нужен стоматолог в центре Калуги\"\n"
        "• \"Ищу детского врача на улице Ленина\"\n"
        "• \"Окулист в Московском районе\"\n\n"
        "⚠️ <i>Я не могу давать медицинские советы или консультации.</i>\n"
        "Для возврата в меню нажмите /start"
    )
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.message(SearchStates.ai_searching)
async def process_ai_query(message: Message, state: FSMContext):
    """Process user query with AI."""
    logger.info(f"AI search query received: {message.text[:50]}...")
    
    user_query = message.text.strip()
    
    if not user_query:
        await message.answer("Пожалуйста, напишите ваш запрос текстом.")
        return
    
    # Get services
    data_service = await get_data_service(message)
    ai_assistant = await get_ai_assistant(message)
    
    if not data_service or not ai_assistant:
        await message.answer(
            "Ошибка сервиса. Попробуйте обычный поиск.",
            reply_markup=build_start_keyboard()
        )
        await state.clear()
        return
    
    # Show typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Get conversation history
        data = await state.get_data()
        conversation_history = data.get('conversation_history', [])
        
        # Get specialties
        specialties_data = await data_service.get_specialties(limit=100)
        specialties = specialties_data.get('items', [])
        
        if not specialties:
            await message.answer(
                "Не удалось загрузить список специальностей.",
                reply_markup=build_start_keyboard()
            )
            await state.clear()
            return
        
        # Get AI response
        result = await ai_assistant.search_doctors(
            user_query=user_query,
            specialties=specialties,
            conversation_history=conversation_history
        )
        
        # Update conversation history
        conversation_history.append({'role': 'user', 'content': user_query})
        conversation_history.append({'role': 'assistant', 'content': result['response']})
        await state.update_data(conversation_history=conversation_history)
        
        # Send AI response
        await message.answer(result['response'], parse_mode="HTML")
        
        # Check if user only provided address without specialty
        location_info = result.get('location_info', {})
        if location_info.get('has_location') and result['needs_clarification']:
            await message.answer(
                "Я вижу, что вы указали адрес, но не понял, какого врача вы ищете. 🤔\n\n"
                "Пожалуйста, уточните специальность, например:\n"
                "• \"Нужен стоматолог на улице Ленина\"\n"
                "• \"Ищу терапевта в центре\""
            )
            return
        
        # Check if AI couldn't find specialty (user asking unrelated questions)
        if result['needs_clarification'] and not location_info.get('has_location'):
            await message.answer(
                "Братан, я тут только врачей ищу, а не на все вопросы отвечаю 😅\n\n"
                "Скажи нормально:\n"
                "• Какой врач нужен (терапевт, стоматолог, окулист)\n"
                "• Где искать (можно указать район или улицу)\n\n"
                "Или жми /start чтобы вернуться в меню."
            )
            return
        
        # If specialty identified, show doctors
        if result['specialty_id'] and not result['needs_clarification']:
            specialty_id = result['specialty_id']
            specialty_name = result['specialty_name']
            location_info = result.get('location_info', {})
            
            # Save to state with AI search flag
            await state.update_data(
                specialty_id=specialty_id,
                specialty_name=specialty_name,
                location_info=location_info,
                using_ai_search=True  # Mark that we're using AI search
            )
            
            # Get hospitals
            hospitals_data = await data_service.get_hospitals(
                specialty_id=specialty_id, limit=100
            )
            hospitals = hospitals_data.get('items', [])
            
            if not hospitals:
                await message.answer(
                    f"К сожалению, не нашел больниц с врачами специальности \"{specialty_name}\".\n\n"
                    "Попробуйте другой запрос или используйте обычный поиск.",
                    reply_markup=build_start_keyboard()
                )
                return
            
            # Filter hospitals by location using AI if specified
            original_count = len(hospitals)
            filtered_applied = False
            
            if location_info.get('has_location'):
                # Use AI to filter hospitals based on real addresses from DB
                filtered_hospitals = await ai_assistant.filter_hospitals_by_location(
                    user_query=user_query,
                    hospitals=hospitals
                )
                
                # Use filtered list if not empty and different from original
                if filtered_hospitals and len(filtered_hospitals) < len(hospitals):
                    hospitals = filtered_hospitals
                    filtered_applied = True
                    logger.info(f"AI filtered hospitals by location: {len(hospitals)}/{original_count} results")
                elif not filtered_hospitals:
                    logger.warning(f"No hospitals matched location filter, showing all {original_count}")
                    # Inform user that no exact matches found
                    await message.answer(
                        "⚠️ Не нашел больниц точно по указанному адресу.\n"
                        "Показываю все доступные варианты:"
                    )
                else:
                    logger.info(f"AI returned same hospitals, no filtering applied")
            
            # Save filtered hospitals list to state for back navigation
            hospital_ids = [h['id'] for h in hospitals]
            logger.info(f"Saving {len(hospital_ids)} hospital IDs to state: {hospital_ids}")
            await state.update_data(
                filtered_hospitals=hospital_ids,
                filter_applied=filtered_applied,
                original_count=original_count
            )
            
            # Show hospitals
            keyboard = build_paginated_keyboard(
                items=hospitals,
                callback_prefix="ai_hospital",
                page=1,
                total_pages=1,
                id_key="id",
                name_key="name",
            )
            
            # Build message with location info
            location_hint = ""
            filter_applied = False
            
            if location_info.get('has_location') and len(hospitals) < original_count:
                filter_applied = True
                if location_info.get('district'):
                    location_hint = f"\n📍 Район: {location_info['district'].title()}"
                elif location_info.get('near_center'):
                    location_hint = "\n📍 Центр города"
                else:
                    # Extract location from query
                    location_words = [w for w in user_query.split() if len(w) > 3]
                    if location_words:
                        location_hint = f"\n📍 Адрес: {' '.join(location_words[:3])}"
            
            # Build message
            if filter_applied:
                message_text = (
                    f"✅ <b>Отфильтровал результаты по вашему запросу!</b>\n\n"
                    f"🏥 <b>Найдено больниц: {len(hospitals)}</b> (из {original_count})\n"
                    f"Специальность: <b>{specialty_name}</b>{location_hint}\n\n"
                    f"Выберите медицинское учреждение:"
                )
            else:
                message_text = (
                    f"🏥 <b>Выберите медицинское учреждение:</b>\n\n"
                    f"Специальность: <b>{specialty_name}</b>\n"
                    f"Найдено: <b>{len(hospitals)}</b> больниц{location_hint}"
                )
            
            await message.answer(
                message_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
            await state.set_state(SearchStates.selecting_hospital)
        
    except Exception as e:
        logger.error(f"Error in AI search: {e}")
        await message.answer(
            "Произошла ошибка при обработке запроса. Попробуйте еще раз или используйте обычный поиск.",
            reply_markup=build_start_keyboard()
        )


@router.message(SearchStates.selecting_doctor)
async def handle_text_during_doctor_selection(message: Message, state: FSMContext):
    """Handle text messages during doctor selection."""
    logger.info(f"Text message during doctor selection: {message.text[:50]}...")
    
    await message.answer(
        "Пожалуйста, выберите врача из списка выше, используя кнопки.\n\n"
        "Или отправьте /start для нового поиска."
    )


@router.callback_query(F.data.startswith("ai_hospital:"))
async def select_ai_hospital(callback: CallbackQuery, state: FSMContext):
    """Handle hospital selection from AI search."""
    hospital_id = int(callback.data.split(":")[1])
    
    try:
        data = await state.get_data()
        specialty_id = data.get("specialty_id")
        specialty_name = data.get("specialty_name")
        
        if not specialty_id:
            await callback.answer("Ошибка: специальность не выбрана", show_alert=True)
            return
        
        # Get data service
        data_service = await get_data_service(callback)
        if not data_service:
            await callback.answer("Ошибка сервиса данных", show_alert=True)
            return
        
        # Get doctors
        doctors_data = await data_service.get_doctors(
            hospital_id=hospital_id, specialty_id=specialty_id, limit=100
        )
        doctors = doctors_data.get('items', [])
        
        if not doctors:
            await callback.answer("Врачи не найдены", show_alert=True)
            return
        
        # Build keyboard
        keyboard = build_paginated_keyboard(
            items=doctors,
            callback_prefix="doctor",
            page=1,
            total_pages=1,
            id_key="id",
            name_key="name",
            back_callback="back_to_ai_hospitals",
        )
        
        # Delete previous message and send new one
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        await callback.message.answer(
            f"👨‍⚕️ <b>Выберите врача:</b>\n\n"
            f"Специальность: <b>{specialty_name}</b>",
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        
        # Store hospital ID
        await state.update_data(hospital_id=hospital_id)
        await state.set_state(SearchStates.selecting_doctor)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error selecting hospital: {e}")
        await callback.answer("Ошибка при загрузке данных", show_alert=True)


@router.message(SearchStates.selecting_hospital)
async def handle_text_during_hospital_selection(message: Message, state: FSMContext):
    """Handle text messages during hospital selection - refine by location."""
    logger.info(f"Refining search with: {message.text[:50]}...")
    
    user_query = message.text.strip()
    
    # Get services
    data_service = await get_data_service(message)
    ai_assistant = await get_ai_assistant(message)
    
    if not data_service or not ai_assistant:
        await message.answer("Ошибка сервиса.")
        return
    
    # Get current search data
    data = await state.get_data()
    specialty_id = data.get('specialty_id')
    specialty_name = data.get('specialty_name')
    
    if not specialty_id:
        await message.answer("Ошибка: специальность не найдена. Начните поиск заново.")
        return
    
    # Show typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Extract location info from new query
        location_info = ai_assistant._extract_location_info(user_query)
        
        if not location_info.get('has_location'):
            await message.answer(
                "Не могу определить адрес или район. 🤔\n\n"
                "Попробуйте указать:\n"
                "• Улицу (например: \"улица Ленина\")\n"
                "• Район (например: \"центр города\")\n"
                "• Ориентир (например: \"рядом с площадью\")"
            )
            return
        
        # Get hospitals for this specialty
        hospitals_data = await data_service.get_hospitals(
            specialty_id=specialty_id, limit=100
        )
        hospitals = hospitals_data.get('items', [])
        
        # Filter by location using AI with real addresses from DB
        filtered_hospitals = await ai_assistant.filter_hospitals_by_location(
            user_query=user_query,
            hospitals=hospitals
        )
        
        if not filtered_hospitals:
            await message.answer(
                f"😔 К сожалению, не нашел больниц с врачами специальности \"{specialty_name}\" "
                f"по указанному адресу.\n\n"
                "Попробуйте:\n"
                "• Указать другой адрес\n"
                "• Выбрать из списка выше\n"
                "• Начать новый поиск /start"
            )
            return
        
        # Update location info and filtered list in state
        await state.update_data(
            location_info=location_info,
            filtered_hospitals=[h['id'] for h in filtered_hospitals],
            filter_applied=True,
            original_count=len(hospitals)
        )
        
        # Show filtered hospitals
        keyboard = build_paginated_keyboard(
            items=filtered_hospitals,
            callback_prefix="ai_hospital",
            page=1,
            total_pages=1,
            id_key="id",
            name_key="name",
        )
        
        location_hint = ""
        if location_info.get('district'):
            location_hint = f"\n📍 Район: {location_info['district'].title()}"
        elif location_info.get('near_center'):
            location_hint = "\n📍 Центр города"
        else:
            location_hint = f"\n📍 {user_query}"
        
        await message.answer(
            f"✅ <b>Отфильтровал результаты по вашему запросу!</b>\n\n"
            f"🏥 <b>Найдено больниц: {len(filtered_hospitals)}</b>\n"
            f"Специальность: <b>{specialty_name}</b>{location_hint}\n\n"
            f"Выберите медицинское учреждение:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        logger.info(f"Filtered hospitals: {len(filtered_hospitals)} results")
        
    except Exception as e:
        logger.error(f"Error refining search: {e}")
        await message.answer(
            "Произошла ошибка при фильтрации. Выберите больницу из списка выше."
        )


@router.callback_query(F.data == "back_to_ai_hospitals")
async def back_to_ai_hospitals(callback: CallbackQuery, state: FSMContext):
    """Go back to hospital selection in AI search - preserve filters."""
    try:
        data = await state.get_data()
        specialty_id = data.get("specialty_id")
        specialty_name = data.get("specialty_name")
        location_info = data.get("location_info", {})
        filtered_hospital_ids = data.get("filtered_hospitals", [])
        filter_applied = data.get("filter_applied", False)
        original_count = data.get("original_count", 0)
        
        if not specialty_id:
            await callback.answer("Ошибка: специальность не выбрана", show_alert=True)
            return
        
        # Get data service
        data_service = await get_data_service(callback)
        if not data_service:
            await callback.answer("Ошибка сервиса данных", show_alert=True)
            return
        
        # Get all hospitals
        hospitals_data = await data_service.get_hospitals(
            specialty_id=specialty_id, limit=100
        )
        all_hospitals = hospitals_data.get('items', [])
        
        # Apply saved filter if exists
        if filtered_hospital_ids:
            logger.info(f"Restoring from saved IDs: {filtered_hospital_ids}")
            hospitals = [h for h in all_hospitals if h['id'] in filtered_hospital_ids]
            logger.info(f"Restored filtered hospitals: {len(hospitals)} from {len(filtered_hospital_ids)} saved IDs")
            logger.info(f"Restored hospital IDs: {[h['id'] for h in hospitals]}")
        else:
            hospitals = all_hospitals
        
        if not hospitals:
            await callback.answer("Больницы не найдены", show_alert=True)
            return
        
        # Build keyboard
        keyboard = build_paginated_keyboard(
            items=hospitals,
            callback_prefix="ai_hospital",
            page=1,
            total_pages=1,
            id_key="id",
            name_key="name",
        )
        
        # Build message with location info
        location_hint = ""
        
        if filter_applied and location_info.get('has_location'):
            if location_info.get('district'):
                location_hint = f"\n📍 Район: {location_info['district'].title()}"
            elif location_info.get('near_center'):
                location_hint = "\n📍 Центр города"
            else:
                location_hint = "\n📍 По указанному адресу"
        
        # Build message
        if filter_applied:
            message_text = (
                f"✅ <b>Отфильтрованные результаты</b>\n\n"
                f"🏥 <b>Найдено больниц: {len(hospitals)}</b> (из {original_count})\n"
                f"Специальность: <b>{specialty_name}</b>{location_hint}\n\n"
                f"Выберите медицинское учреждение:"
            )
        else:
            message_text = (
                f"🏥 <b>Выберите медицинское учреждение:</b>\n\n"
                f"Специальность: <b>{specialty_name}</b>\n"
                f"Найдено: <b>{len(hospitals)}</b> больниц"
            )
        
        # Delete previous message and send new one
        try:
            await callback.message.delete()
        except Exception:
            pass
        
        await callback.message.answer(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        
        await state.set_state(SearchStates.selecting_hospital)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error going back to hospitals: {e}")
        await callback.answer("Ошибка при загрузке данных", show_alert=True)
