"""AI Assistant service using GigaChat."""

import logging
import re
from typing import Dict, List, Any, Optional
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

logger = logging.getLogger(__name__)


class AIAssistant:
    """AI Assistant for doctor search using GigaChat."""
    
    def __init__(self, credentials: str):
        """Initialize AI Assistant.
        
        Args:
            credentials: GigaChat API credentials
        """
        self.credentials = credentials
        self.client = None
        
    async def initialize(self):
        """Initialize GigaChat client."""
        try:
            # Try different initialization approaches
            # Approach 1: Direct credentials with scope and timeout
            try:
                self.client = GigaChat(
                    credentials=self.credentials,
                    verify_ssl_certs=False,
                    scope="GIGACHAT_API_PERS",
                    timeout=30.0  # 30 seconds timeout
                )
                logger.info("GigaChat client initialized successfully with scope")
                return
            except Exception as e1:
                logger.warning(f"Failed with scope parameter: {e1}")
            
            # Approach 2: Without scope
            try:
                self.client = GigaChat(
                    credentials=self.credentials,
                    verify_ssl_certs=False
                )
                logger.info("GigaChat client initialized successfully without scope")
                return
            except Exception as e2:
                logger.warning(f"Failed without scope: {e2}")
                raise e2
                
        except Exception as e:
            logger.error(f"Failed to initialize GigaChat: {e}")
            raise
    
    async def filter_hospitals_by_location(
        self,
        user_query: str,
        hospitals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter hospitals by location using AI understanding.
        
        Args:
            user_query: User's location query
            hospitals: List of hospitals with addresses
            
        Returns:
            Filtered list of hospitals
        """
        if not hospitals:
            return []
        
        # Extract location info
        location_info = self._extract_location_info(user_query)
        
        if not location_info.get('has_location'):
            return hospitals
        
        # Build list of addresses for AI
        addresses_list = "\n".join([
            f"{i+1}. {h.get('name', 'Неизвестно')}: {h.get('address', 'Адрес не указан')}"
            for i, h in enumerate(hospitals[:50])  # Limit to 50 for AI processing
        ])
        
        system_prompt = f"""Ты - помощник по фильтрации адресов в городе Калуга.

Список больниц с адресами:
{addresses_list}

Запрос пользователя: "{user_query}"

Твоя задача:
1. Определить ВСЕ адреса в КАЛУГЕ, которые соответствуют запросу пользователя
2. Вернуть ТОЛЬКО номера ВСЕХ подходящих больниц через запятую

КРИТИЧЕСКИ ВАЖНО:
- Рассматривай ТОЛЬКО адреса, где указан город КАЛУГА
- ИГНОРИРУЙ все адреса в других городах (Москва, Обнинск, Тула и т.д.)
- Если в адресе нет слова "КАЛУГА" - НЕ включай эту больницу

Фильтрация по районам Калуги:
- "в центре" / "центр города" / "центр Калуги" = улицы: Ленина, Кирова, Театральная, Октябрьская, Площадь, Баумана, Суворова
- "Московский район" = адреса с указанием "Московский" или улицы в этом районе
- Включай ВСЕ больницы в Калуге, которые подходят под запрос

Примеры:
- Запрос "в центре Калуги" → ВСЕ больницы с адресами "КАЛУГА" + центральные улицы: 1,3,5,7,12,15
- Запрос "улица Ленина" → ВСЕ больницы "КАЛУГА, ул. Ленина": 2,8,14
- Запрос "Московский район" → ВСЕ больницы "КАЛУГА, Московский": 4,9,11,16

ИСКЛЮЧАЙ:
- Адреса без слова "КАЛУГА"
- Адреса в других городах (даже если улица подходит)

Ответь ТОЛЬКО номерами через запятую, например: 1,3,5,7,12,15"""

        messages = [
            Messages(role=MessagesRole.SYSTEM, content=system_prompt),
            Messages(role=MessagesRole.USER, content=f"Какие больницы подходят под запрос: {user_query}?")
        ]
        
        try:
            if not self.client:
                await self.initialize()
            
            response = self.client.chat(Chat(messages=messages))
            ai_response = response.choices[0].message.content.strip()
            
            logger.info(f"AI address filtering response: {ai_response}")
            
            # Parse numbers from response
            numbers = re.findall(r'\d+', ai_response)
            selected_indices = [int(n) - 1 for n in numbers if int(n) <= len(hospitals)]
            
            if selected_indices:
                filtered = [hospitals[i] for i in selected_indices if i < len(hospitals)]
                
                # Log selected addresses for debugging
                for h in filtered:
                    logger.info(f"AI selected: {h.get('name')} - Address: {h.get('address', 'NO ADDRESS')}")
                
                # Additional filter: ensure addresses contain "Калуга" or "КАЛУГА"
                filtered_kaluga = [
                    h for h in filtered 
                    if h.get('address') and ('калуга' in h.get('address', '').lower() or 'kaluga' in h.get('address', '').lower())
                ]
                
                if filtered_kaluga:
                    logger.info(f"AI filtered {len(filtered_kaluga)} hospitals in Kaluga from {len(hospitals)}")
                    return filtered_kaluga
                else:
                    logger.warning(f"AI filtered {len(filtered)} hospitals but none in Kaluga")
                    logger.warning(f"Sample addresses: {[h.get('address', 'NO ADDR')[:50] for h in filtered[:3]]}")
                    # Return filtered anyway - AI knows better
                    return filtered
            else:
                logger.warning("AI didn't return valid hospital numbers")
                return hospitals
                
        except Exception as e:
            logger.error(f"Error in AI address filtering: {e}")
            # Fallback to simple matching
            return [h for h in hospitals if self.match_address(h.get('address', ''), user_query)]
    
    async def search_doctors(
        self, 
        user_query: str, 
        specialties: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Search for doctors using AI.
        
        Args:
            user_query: User's natural language query
            specialties: List of available specialties
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary with search results and AI response
        """
        if not self.client:
            await self.initialize()
        
        # Prepare specialty list for AI
        specialty_list = "\n".join([f"- {s['name']} (ID: {s['id']})" for s in specialties])
        
        # Build system prompt with enhanced capabilities
        system_prompt = f"""Ты - умный помощник по поиску врачей в медицинских учреждениях Калуги.

Доступные специальности:
{specialty_list}

Твои возможности:
1. Понимать запросы о специальностях врачей
2. Распознавать адреса, районы и улицы Калуги
3. Учитывать предпочтения пользователя (близко к дому, хорошие отзывы)
4. Предлагать альтернативы, если точной специальности нет

Примеры запросов:
- "Нужен окулист рядом с улицей Ленина"
- "Ищу хорошего стоматолога в центре"
- "Детский врач недалеко от дома"

Твоя задача:
1. Определить специальность из списка выше
2. Извлечь информацию о местоположении (адрес, район, улица)
3. Понять предпочтения (близко, хорошие отзывы, опытный)
4. Ответить дружелюбно и помочь с поиском

Формат ответа:
- Подтверди, что понял запрос
- Укажи найденную специальность
- Если есть адрес - упомяни его
- Предложи помощь в выборе

Отвечай кратко и по делу. Используй эмодзи для дружелюбности."""

        # Build messages
        messages = [
            Messages(role=MessagesRole.SYSTEM, content=system_prompt)
        ]
        
        # Add conversation history if exists
        if conversation_history:
            for msg in conversation_history[-4:]:  # Last 4 messages for context
                role = MessagesRole.USER if msg['role'] == 'user' else MessagesRole.ASSISTANT
                messages.append(Messages(role=role, content=msg['content']))
        
        # Add current query
        messages.append(Messages(role=MessagesRole.USER, content=user_query))
        
        try:
            # Extract location info from user query
            location_info = self._extract_location_info(user_query)
            
            # Get AI response with timeout handling
            logger.info(f"Sending request to GigaChat for query: {user_query[:50]}...")
            response = self.client.chat(Chat(messages=messages))
            ai_response = response.choices[0].message.content
            logger.info(f"Received response from GigaChat: {ai_response[:50]}...")
            
            # Extract specialty from response
            specialty_id = self._extract_specialty_id(ai_response, specialties)
            
            # Enhance response with location info
            if location_info['has_location'] and specialty_id:
                ai_response += "\n\n✅ <b>Применяю фильтр по местоположению:</b>"
                
                if location_info['district']:
                    ai_response += f"\n📍 Район: {location_info['district'].title()}"
                elif location_info['near_center']:
                    ai_response += f"\n📍 Центр города"
                else:
                    ai_response += f"\n📍 По указанному адресу"
                
                if 'nearby' in location_info['preferences']:
                    ai_response += "\n🚶 Приоритет: близость к дому"
                
                if 'quality' in location_info['preferences']:
                    ai_response += "\n⭐ Приоритет: качество и репутация"
                
                ai_response += "\n\nПоказываю только подходящие варианты! 🎯"
            
            return {
                "response": ai_response,
                "specialty_id": specialty_id,
                "specialty_name": next((s['name'] for s in specialties if s['id'] == specialty_id), None) if specialty_id else None,
                "needs_clarification": specialty_id is None,
                "location_info": location_info
            }
            
        except Exception as e:
            logger.error(f"Error in AI search: {e}")
            return {
                "response": "Извините, произошла ошибка. Попробуйте использовать обычный поиск через кнопки.",
                "specialty_id": None,
                "specialty_name": None,
                "needs_clarification": True,
                "location_info": {},
                "error": str(e)
            }
    
    def _extract_specialty_id(self, ai_response: str, specialties: List[Dict[str, Any]]) -> Optional[int]:
        """Extract specialty ID from AI response.
        
        Args:
            ai_response: AI's response text
            specialties: List of available specialties
            
        Returns:
            Specialty ID if found, None otherwise
        """
        # Look for specialty mentions in response
        response_lower = ai_response.lower()
        
        for specialty in specialties:
            specialty_name_lower = specialty['name'].lower()
            if specialty_name_lower in response_lower:
                return specialty['id']
        
        # Check for common synonyms
        synonyms = {
            'окулист': 'офтальмолог',
            'глазной': 'офтальмолог',
            'зубной': 'стоматолог',
            'дантист': 'стоматолог',
            'детский врач': 'педиатр',
            'лор': 'оториноларинголог',
            'ухо-горло-нос': 'оториноларинголог',
            'ухогорлонос': 'оториноларинголог',
            'невролог': 'невролог',
            'психиатр': 'психиатр',
            'хирург': 'хирург',
            'терапевт': 'терапевт'
        }
        
        for synonym, specialty_name in synonyms.items():
            if synonym in response_lower:
                for specialty in specialties:
                    if specialty_name.lower() in specialty['name'].lower():
                        return specialty['id']
        
        return None
    
    def match_address(self, hospital_address: str, location_query: str) -> bool:
        """Check if hospital address matches location query.
        
        Args:
            hospital_address: Hospital's address
            location_query: User's location query
            
        Returns:
            True if address matches query
        """
        address_lower = hospital_address.lower()
        query_lower = location_query.lower()
        
        # Extract location info
        location_info = self._extract_location_info(location_query)
        
        # Check district
        if location_info.get('district'):
            if location_info['district'] in address_lower:
                return True
        
        # Check center
        if location_info.get('near_center'):
            center_keywords = ['центр', 'ленина', 'кирова', 'театральная', 'площадь', 'октябрьская']
            if any(keyword in address_lower for keyword in center_keywords):
                return True
        
        # Check for street names and numbers
        # Extract words longer than 3 characters
        query_words = [w for w in query_lower.split() if len(w) > 3 and w not in [
            'улица', 'улице', 'проспект', 'переулок', 'район', 'рядом', 'около', 
            'возле', 'недалеко', 'близко', 'нужен', 'ищу', 'найти'
        ]]
        
        # Check if any significant word from query is in address
        matches = sum(1 for word in query_words if word in address_lower)
        
        # If at least 1 significant word matches, consider it a match
        return matches > 0
    
    def _extract_location_info(self, user_query: str) -> Dict[str, Any]:
        """Extract location information from user query.
        
        Args:
            user_query: User's query text
            
        Returns:
            Dictionary with location info (address, district, preferences)
        """
        query_lower = user_query.lower()
        
        # Common location keywords
        location_keywords = [
            'улица', 'ул.', 'проспект', 'пр.', 'переулок', 'пер.',
            'район', 'рядом', 'около', 'возле', 'недалеко', 'близко',
            'центр', 'центре', 'окраина'
        ]
        
        # Districts of Kaluga
        districts = [
            'ленинский', 'московский', 'октябрьский',
            'центр', 'центральный'
        ]
        
        # Extract location info
        location_info = {
            'has_location': False,
            'address': None,
            'district': None,
            'near_center': False,
            'preferences': []
        }
        
        # Check for location keywords
        for keyword in location_keywords:
            if keyword in query_lower:
                location_info['has_location'] = True
                break
        
        # Check for districts
        for district in districts:
            if district in query_lower:
                location_info['district'] = district
                location_info['has_location'] = True
        
        # Check for center
        if 'центр' in query_lower:
            location_info['near_center'] = True
            location_info['has_location'] = True
        
        # Extract preferences
        if any(word in query_lower for word in ['хороший', 'лучший', 'опытный', 'проверенный']):
            location_info['preferences'].append('quality')
        
        if any(word in query_lower for word in ['близко', 'рядом', 'недалеко', 'около']):
            location_info['preferences'].append('nearby')
        
        if any(word in query_lower for word in ['отзыв', 'рейтинг', 'рекомендуют']):
            location_info['preferences'].append('reviews')
        
        return location_info
    
    async def get_recommendation(
        self,
        doctors: List[Dict[str, Any]],
        user_preferences: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        location_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get AI recommendation for doctors.
        
        Args:
            doctors: List of doctors with their info
            user_preferences: User's preferences or question
            conversation_history: Previous conversation
            location_info: Location preferences from search
            
        Returns:
            AI recommendation text
        """
        if not self.client:
            await self.initialize()
        
        # Prepare doctors info with addresses
        doctors_info = "\n\n".join([
            f"Врач {i+1}: {d['name']}\n"
            f"Больница: {d.get('hospital_name', 'Не указана')}\n"
            f"Адрес: {d.get('address', 'Не указан')}\n"
            f"Специальность: {d.get('specialty_name', 'Не указана')}"
            for i, d in enumerate(doctors[:5])  # Top 5 doctors
        ])
        
        location_context = ""
        if location_info and location_info.get('has_location'):
            location_context = "\n\nПредпочтения пользователя по местоположению:\n"
            if location_info.get('district'):
                location_context += f"- Район: {location_info['district']}\n"
            if location_info.get('near_center'):
                location_context += "- Предпочитает центр города\n"
            if 'nearby' in location_info.get('preferences', []):
                location_context += "- Важна близость к дому\n"
            if 'quality' in location_info.get('preferences', []):
                location_context += "- Важно качество и репутация\n"
        
        system_prompt = f"""Ты - умный помощник по выбору врача в Калуге.

Доступные врачи:
{doctors_info}{location_context}

Твоя задача:
1. Учесть предпочтения пользователя (местоположение, качество)
2. Порекомендовать наиболее подходящего врача
3. Объяснить, почему именно этот врач подходит
4. Упомянуть адрес и удобство расположения

Отвечай кратко, дружелюбно и по делу. Используй эмодзи."""

        messages = [
            Messages(role=MessagesRole.SYSTEM, content=system_prompt)
        ]
        
        if conversation_history:
            for msg in conversation_history[-4:]:
                role = MessagesRole.USER if msg['role'] == 'user' else MessagesRole.ASSISTANT
                messages.append(Messages(role=role, content=msg['content']))
        
        messages.append(Messages(role=MessagesRole.USER, content=user_preferences))
        
        try:
            response = self.client.chat(Chat(messages=messages))
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting recommendation: {e}")
            return "Извините, не могу дать рекомендацию. Выберите врача из списка."
    
    async def close(self):
        """Close GigaChat client."""
        if self.client:
            # GigaChat client doesn't need explicit closing
            self.client = None
            logger.info("GigaChat client closed")
