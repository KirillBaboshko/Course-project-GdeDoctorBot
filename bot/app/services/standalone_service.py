"""Standalone bot data service - works without backend."""

import sqlite3
import aiohttp
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class StandaloneDataService:
    """Standalone data service that works directly with SQLite database."""
    
    def __init__(self, db_path: str = "medical_data.db", yandex_api_key: str = ""):
        """Initialize standalone data service.
        
        Args:
            db_path: Path to SQLite database
            yandex_api_key: Yandex Maps API key
        """
        self.db_path = db_path
        self.yandex_api_key = yandex_api_key
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for Yandex API."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _get_db_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        db_file = Path(self.db_path)
        if not db_file.exists():
            logger.warning(f"Database file {self.db_path} not found. Creating empty database.")
            # Create empty database with basic structure
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS specialties (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hospitals (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    address TEXT,
                    specialty_id INTEGER,
                    FOREIGN KEY (specialty_id) REFERENCES specialties (id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    hospital_id INTEGER,
                    specialty_id INTEGER,
                    FOREIGN KEY (hospital_id) REFERENCES hospitals (id),
                    FOREIGN KEY (specialty_id) REFERENCES specialties (id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY,
                    doctor_id INTEGER,
                    hospital_id INTEGER,
                    user_name TEXT,
                    review_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (doctor_id) REFERENCES doctors (id),
                    FOREIGN KEY (hospital_id) REFERENCES hospitals (id)
                )
            """)
            conn.commit()
            return conn
        
        return sqlite3.connect(self.db_path)
    
    async def get_specialties(self, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Get list of specialties."""
        conn = self._get_db_connection()
        try:
            cursor = conn.execute(
                "SELECT id, name FROM specialties ORDER BY name LIMIT ? OFFSET ?",
                (limit, skip)
            )
            specialties = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
            
            # Get total count
            cursor = conn.execute("SELECT COUNT(*) FROM specialties")
            total = cursor.fetchone()[0]
            
            return {
                "items": specialties,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        finally:
            conn.close()
    
    async def get_hospitals(self, specialty_id: Optional[int] = None, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Get list of hospitals."""
        conn = self._get_db_connection()
        try:
            if specialty_id:
                # Get hospitals that have doctors with this specialty
                cursor = conn.execute(
                    """SELECT DISTINCT h.id, h.name
                       FROM hospitals h
                       JOIN doctor_work_placements dwp ON h.id = dwp.hospital_id
                       WHERE dwp.specialty_id = ?
                       ORDER BY h.name LIMIT ? OFFSET ?""",
                    (specialty_id, limit, skip)
                )
                cursor_count = conn.execute(
                    """SELECT COUNT(DISTINCT h.id)
                       FROM hospitals h
                       JOIN doctor_work_placements dwp ON h.id = dwp.hospital_id
                       WHERE dwp.specialty_id = ?""",
                    (specialty_id,)
                )
            else:
                cursor = conn.execute(
                    "SELECT id, name FROM hospitals ORDER BY name LIMIT ? OFFSET ?",
                    (limit, skip)
                )
                cursor_count = conn.execute("SELECT COUNT(*) FROM hospitals")
            
            hospitals = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
            total = cursor_count.fetchone()[0]
            
            return {
                "items": hospitals,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        finally:
            conn.close()
    
    async def get_doctors(self, hospital_id: int, specialty_id: int, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Get list of doctors."""
        conn = self._get_db_connection()
        try:
            cursor = conn.execute(
                """SELECT d.id, d.full_name, h.name as hospital_name, s.name as specialty_name
                   FROM doctors d
                   JOIN doctor_work_placements dwp ON d.id = dwp.doctor_id
                   JOIN hospitals h ON dwp.hospital_id = h.id
                   JOIN specialties s ON dwp.specialty_id = s.id
                   WHERE dwp.hospital_id = ? AND dwp.specialty_id = ?
                   ORDER BY d.full_name LIMIT ? OFFSET ?""",
                (hospital_id, specialty_id, limit, skip)
            )
            doctors = [
                {
                    "id": row[0],
                    "name": row[1],
                    "hospital_name": row[2],
                    "specialty_name": row[3]
                }
                for row in cursor.fetchall()
            ]
            
            cursor = conn.execute(
                """SELECT COUNT(*)
                   FROM doctor_work_placements
                   WHERE hospital_id = ? AND specialty_id = ?""",
                (hospital_id, specialty_id)
            )
            total = cursor.fetchone()[0]
            
            return {
                "items": doctors,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        finally:
            conn.close()
    
    async def get_doctor(self, doctor_id: int, hospital_id: int) -> Dict[str, Any]:
        """Get doctor details."""
        conn = self._get_db_connection()
        try:
            cursor = conn.execute(
                """SELECT d.id, d.full_name, h.name as hospital_name, a.full_address, s.name as specialty_name
                   FROM doctors d
                   JOIN doctor_work_placements dwp ON d.id = dwp.doctor_id
                   JOIN hospitals h ON dwp.hospital_id = h.id
                   JOIN specialties s ON dwp.specialty_id = s.id
                   LEFT JOIN hospital_addresses ha ON h.id = ha.hospital_id
                   LEFT JOIN addresses a ON ha.address_id = a.id
                   WHERE d.id = ? AND dwp.hospital_id = ?
                   LIMIT 1""",
                (doctor_id, hospital_id)
            )
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"Doctor {doctor_id} not found")
            
            return {
                "id": row[0],
                "name": row[1],
                "hospital_name": row[2],
                "address": row[3] if row[3] else "Адрес не указан",
                "specialty_name": row[4]
            }
        finally:
            conn.close()
    
    async def search_doctors(self, name: str) -> List[Dict[str, Any]]:
        """Search doctors by name."""
        conn = self._get_db_connection()
        try:
            cursor = conn.execute(
                """SELECT d.id, d.name, h.name as hospital_name, s.name as specialty_name, h.id as hospital_id
                   FROM doctors d
                   JOIN hospitals h ON d.hospital_id = h.id
                   JOIN specialties s ON d.specialty_id = s.id
                   WHERE d.name LIKE ? ORDER BY d.name""",
                (f"%{name}%",)
            )
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "hospital_name": row[2],
                    "specialty_name": row[3],
                    "hospital_id": row[4]
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
    
    async def get_reviews(self, doctor_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get reviews."""
        conn = self._get_db_connection()
        try:
            if doctor_id:
                cursor = conn.execute(
                    "SELECT id, user_name, review_text, created_at FROM doctor_reviews WHERE doctor_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (doctor_id, limit, skip)
                )
            else:
                cursor = conn.execute(
                    "SELECT id, user_name, review_text, created_at FROM doctor_reviews ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, skip)
                )
            
            return [
                {
                    "id": row[0],
                    "user_name": row[1],
                    "review_text": row[2],
                    "created_at": row[3]
                }
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
    
    async def create_review(self, doctor_id: int, hospital_id: int, user_name: str, review_text: str) -> Dict[str, Any]:
        """Create a review."""
        conn = self._get_db_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO doctor_reviews (doctor_id, hospital_id, user_name, review_text) VALUES (?, ?, ?, ?)",
                (doctor_id, hospital_id, user_name, review_text)
            )
            conn.commit()
            return {"id": cursor.lastrowid, "message": "Review created successfully"}
        finally:
            conn.close()
    
    async def geocode(self, address: str) -> Dict[str, Any]:
        """Geocode address using Yandex API."""
        if not self.yandex_api_key:
            raise ValueError("Yandex API key is required for geocoding")
        
        session = await self.get_session()
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": self.yandex_api_key,
            "geocode": address,
            "format": "json",
            "results": 1
        }
        
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            
            try:
                geo_object = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                pos = geo_object["Point"]["pos"].split()
                lon, lat = float(pos[0]), float(pos[1])
                
                return {
                    "lon": lon,
                    "lat": lat,
                    "address": geo_object["metaDataProperty"]["GeocoderMetaData"]["text"]
                }
            except (KeyError, IndexError, ValueError) as e:
                raise ValueError(f"Failed to parse geocoding response: {e}")
    
    async def get_static_map(self, lon: float, lat: float, point: bool = True) -> bytes:
        """Get static map image from Yandex.
        
        Note: Static Maps API v1 does NOT require API key in parameters.
        It works without authentication for basic usage.
        """
        session = await self.get_session()
        url = "https://static-maps.yandex.ru/1.x/"
        params = {
            "ll": f"{lon},{lat}",
            "size": "400,300",
            "z": "15",
            "l": "map"
        }
        
        if point:
            params["pt"] = f"{lon},{lat},pm2rdm"
        
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.read()
