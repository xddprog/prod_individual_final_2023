from sqlalchemy import update, delete
from datetime import datetime

from .connection import session_factory, engine
from .models import Base, User, Travel, Point, Note


class Database:
    @staticmethod
    async def create_tables():
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def create_user(data: dict) -> None:
        async with session_factory() as session:
            user = User(**data)
            session.add(user)
            await session.flush()
            await session.commit()

    @staticmethod
    async def get_user(user_id: int, return_user: bool = False) -> bool:
        async with session_factory() as session:
            user = await session.get(User, user_id)
            return bool(user) if not return_user else user

    @staticmethod
    async def update_user_profile(user_id: int, **data) -> None:
        async with session_factory() as session:
            query = update(User).where(User.user_id == user_id).values(data)
            await session.execute(query)
            await session.flush()
            await session.commit()

    @staticmethod
    async def create_travel(data: dict, user_id: int):
        async with session_factory() as session:
            user = await session.get(User, user_id)
            travel = Travel(
                travel_mode=data['mode'],
                name=data['name'],
                description=data['description']
            )
            start_point = Point(
                address=user.full_address,
                start_date=data['start_travel_date'],
            )
            end_point = Point(
                address=data['address'],
                start_date=data['start_date'],
                end_date=data['end_date'],
            )
            travel.points.append(start_point)
            travel.points.append(end_point)
            user.travels.append(travel)
            session.add(user)
            await session.flush()
            await session.commit()

    @staticmethod
    async def get_travel(travel_id: int) -> Travel:
        async with session_factory() as session:
            travel = await session.get(Travel, int(travel_id))
            return travel

    @staticmethod
    async def create_travel_note(
        travel_id: int,
        author_id: int,
        author_name: str,
        is_private: bool,
        name: str,
        description: str,
        file_id: str,
        content_type: str
    ) -> None:
        async with session_factory() as session:
            travel = await session.get(Travel, travel_id)
            note = Note(
                author_id=author_id,
                author_name=author_name,
                is_private=is_private,
                name=name,
                description=description,
                file_id=file_id,
                created_date=datetime.now(),
                content_type=content_type
            )
            travel.notes.append(note)
            session.add(travel)
            await session.flush()
            await session.commit()

    @staticmethod
    async def get_note(note_id: int) -> Note:
        async with session_factory() as session:
            note = await session.get(Note, note_id)
            return note

    @staticmethod
    async def delete_travel(travel_id: int, user_id: int) -> None:
        async with session_factory() as session:
            user = await session.get(User, user_id)
            for index, travel in enumerate(user.travels):
                if travel.travel_id == travel_id:
                    user.travels.pop(index)
                    session.add(user)
                    await session.flush()
                    await session.commit()
                    break

    @staticmethod
    async def update_note(note_id: int, update_param: str = None, update_value: str = None, **data) -> None:
        async with session_factory() as session:
            if update_param and update_value:
                query = update(Note).where(Note.id == note_id).values(
                    {update_param: update_value},
                ).values(data)
                print(1)
            else:
                query = update(Note).where(Note.id == note_id).values(data)
                print(2)
            print(query)
            await session.execute(query)
            await session.flush()
            await session.commit()

    @staticmethod
    async def delete_note(note_id: int) -> None:
        async with session_factory() as session:
            note = await session.get(Note, note_id)
            await session.delete(note)
            await session.flush()
            await session.commit()
