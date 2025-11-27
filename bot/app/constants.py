"""Text constants for bot messages."""


class Messages:
    """Bot message templates."""

    # Welcome and help
    WELCOME = (
        "👋 <b>Добро пожаловать в GdeDoctor!</b>\n\n"
        "Я помогу вам найти врача в медицинских учреждениях Калуги.\n\n"
        "Что вы хотите сделать?"
    )

    HELP = (
        "📋 <b>Справка по использованию бота</b>\n\n"
        "<b>🔍 Поиск врача:</b>\n"
        "1. Выберите специальность врача\n"
        "2. Выберите медицинское учреждение\n"
        "3. Выберите врача из списка\n"
        "4. Посмотрите информацию и местоположение\n\n"
        "<b>📝 Отзывы:</b>\n"
        "• Читайте отзывы других пациентов\n"
        "• Оставляйте свои отзывы о врачах\n\n"
        "<b>🗺 Карта:</b>\n"
        "• Смотрите местоположение на Яндекс.Картах\n"
        "• Прокладывайте маршрут до клиники"
    )

    CANCEL_MESSAGE = "❌ Действие отменено.\n\nЧто вы хотите сделать?"
    CANCEL_COMMAND = "❌ Действие отменено.\n\nИспользуйте /start для начала работы."
    NOTHING_TO_CANCEL = "Нечего отменять."

    # Search flow
    SEARCH_HEADER = "🔍 <b>Поиск врача</b>\n\n"
    SEARCH_STEP_1 = "Шаг 1 из 3: Выберите специальность врача"
    SEARCH_STEP_2 = "Шаг 2 из 3: Выберите медицинское учреждение"
    SEARCH_STEP_3 = "Шаг 3 из 3: Выберите врача"

    SPECIALTY_SELECTED = "Специальность: <b>{specialty}</b>\n\n"
    HOSPITAL_SELECTED = "Учреждение: <b>{hospital}</b>\n\n"

    # Doctor card
    DOCTOR_CARD = (
        "👨‍⚕️ <b>{full_name}</b>\n\n🏥 {hospital}\n💼 {specialty}\n📍 {address}"
    )

    DOCTOR_CARD_NO_MAP = (
        "👨‍⚕️ <b>{full_name}</b>\n\n"
        "🏥 {hospital}\n"
        "💼 {specialty}\n"
        "📍 {address}\n\n"
        "⚠️ Не удалось загрузить карту"
    )

    # Reviews
    REVIEWS_HEADER = "📝 <b>Отзывы о враче</b>\n\n"
    REVIEWS_EMPTY = "Отзывов пока нет. Будьте первым!"
    REVIEW_ITEM = "👤 <b>{user}</b> ({date})\n{text}\n\n"

    WRITE_REVIEW_PROMPT = (
        "✍️ <b>Оставить отзыв</b>\n\n"
        "Напишите ваш отзыв о враче.\n"
        "Минимум 10 символов, максимум 2000."
    )

    REVIEW_TOO_SHORT = (
        "❌ Отзыв слишком короткий. Минимум 10 символов.\n"
        "Попробуйте еще раз или используйте /cancel для отмены."
    )

    REVIEW_TRUNCATED = "⚠️ Отзыв обрезан до 2000 символов."

    REVIEW_SUCCESS = (
        "✅ <b>Спасибо за ваш отзыв!</b>\n\n"
        "Ваш отзыв успешно сохранен и будет полезен другим пациентам."
    )

    REVIEW_DUPLICATE = (
        "❌ Вы уже оставляли отзыв об этом враче за последние 24 часа.\n"
        "Попробуйте позже."
    )

    REVIEW_ERROR_NO_DOCTOR = (
        "❌ Ошибка: не найдена информация о враче.\nНачните поиск заново с /start"
    )

    # Errors
    ERROR_LOADING_DATA = "Ошибка при загрузке данных"
    ERROR_SAVING_REVIEW = (
        "❌ Ошибка при сохранении отзыва.\n"
        "Попробуйте позже или обратитесь к администратору."
    )
    ERROR_INVALID_FORMAT = "Неверный формат данных"
    ERROR_GEOCODING = "Ошибка при определении координат"
    ERROR_MAP_LOADING = "Ошибка при загрузке карты"

    # Not found messages
    NOT_FOUND_SPECIALTIES = "Специальности не найдены"
    NOT_FOUND_SPECIALTY = "Специальность не найдена"
    NOT_FOUND_HOSPITALS = "Больницы не найдены"
    NOT_FOUND_HOSPITAL = "Больница не найдена"
    NOT_FOUND_HOSPITALS_FOR_SPECIALTY = "Для этой специальности нет больниц"
    NOT_FOUND_DOCTORS = "Врачи не найдены"
    NOT_FOUND_DOCTOR = "Врач не найден"
    NOT_FOUND_DOCTORS_FOR_HOSPITAL = "В этой больнице нет врачей данной специальности"
    NOT_FOUND_REVIEWS = "Информация о враче не найдена"


class ButtonLabels:
    """Button labels for inline keyboards."""

    # Main menu
    FIND_DOCTOR = "🔍 Найти врача"
    HELP = "ℹ️ Помощь"

    # Navigation
    BACK = "◀️ Назад"
    BACK_TO_LIST = "◀️ Назад к списку"
    BACK_TO_DOCTOR = "◀️ Назад к врачу"
    BACK_TO_SPECIALTIES = "◀️ К специальностям"
    BACK_TO_HOSPITALS = "◀️ К больницам"
    HOME = "🏠 В начало"
    CANCEL = "❌ Отмена"

    # Pagination
    PREV = "◀️ Назад"
    NEXT = "Вперед ▶️"

    # Doctor actions
    VIEW_REVIEWS = "📝 Отзывы"
    WRITE_REVIEW = "✍️ Оставить отзыв"
    VIEW_ON_MAP = "🗺 Открыть на карте"
    NEW_SEARCH = "🔍 Новый поиск"


class LogMessages:
    """Log message templates."""

    # Bot lifecycle
    BOT_STARTING = "Starting bot..."
    BOT_STOPPED = "Bot stopped"
    BOT_STOPPED_BY_USER = "Bot stopped by user"
    BOT_API_URL = "API URL: {url}"

    # Errors
    ERROR_GETTING_SPECIALTIES = "Error getting specialties: {error}"
    ERROR_SELECTING_SPECIALTY = "Error selecting specialty: {error}"
    ERROR_SELECTING_HOSPITAL = "Error selecting hospital: {error}"
    ERROR_SELECTING_DOCTOR = "Error selecting doctor: {error}"
    ERROR_GEOCODING = "Error geocoding: {error}"
    ERROR_LOADING_MAP = "Error loading map: {error}"
    ERROR_SHOWING_REVIEWS = "Error showing reviews: {error}"
    ERROR_CREATING_REVIEW = "Error creating review: {error}"
    ERROR_GOING_BACK = "Error going back to {target}: {error}"
    ERROR_PAGINATION = "Error handling pagination: {error}"
    ERROR_SHOWING_DOCTOR_CARD = "Error showing doctor card: {error}"


class Limits:
    """Validation limits."""

    REVIEW_MIN_LENGTH = 10
    REVIEW_MAX_LENGTH = 2000


# Export all constants
__all__ = ["Messages", "ButtonLabels", "LogMessages", "Limits"]
