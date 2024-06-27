from aiohttp import ClientSession

from config import ua
from crud import write_data
from engine import database_sync, db_engine, settings
from models import Areas


def get_dict_(d: dict) -> dict:
    try:
        result = {
            'id': int(d.get('id')),
            'parent_id': int(d.get('parent_id')),
            'name': d.get('name')
        }
    except TypeError:
        result = {
            'id': int(d.get('id')),
            'parent_id': None,
            'name': d.get('name')
        }
    return result


async def get_areas(aio_session: ClientSession):
    await database_sync(engine=db_engine, db_settings=settings, base=Areas)
    URL = 'https://api.hh.ru/areas'
    async with aio_session.get(url=URL, headers={'user-agent': ua.random}) as response:
        data = await response.json()
    async with db_engine.scoped_session() as session:
        for line in data:
            areas = line.get('areas')
            if areas:
                for area in areas:
                    areas_ = area.get('areas')
                    if areas_:
                        for area_ in areas_:
                            await write_data(session=session, table=Areas, data=get_dict_(area_))
                    await write_data(session=session, table=Areas, data=get_dict_(area))
            await write_data(session=session, table=Areas, data=get_dict_(line))
