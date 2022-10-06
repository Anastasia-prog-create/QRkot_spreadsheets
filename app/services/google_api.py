from datetime import datetime
from http import HTTPStatus
from operator import itemgetter
from typing import List

from aiogoogle import Aiogoogle
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.charity_project import CharityProjectDB

FORMAT = "%Y/%m/%d %H:%M:%S"

ROWS = 100
COLUMNS = 11

TABLE_SIZE_ERROR = 'Максимальное количество строк в таблице {}.'


def create_spreadsheet_body(datetime):
    return {
        'properties': {
            'title': f'Отчет на {datetime}',
            'locale': 'ru_RU'
        },
        'sheets': [{
            'properties': {'sheetType': 'GRID',
                           'sheetId': 0,
                           'title': 'Лист1',
                           'gridProperties': {'rowCount': ROWS,
                                              'columnCount': COLUMNS}}
        }]
    }


def creat_table_head(datetime):
    return [
        ['Отчет от', f'{datetime}'],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
#  Мне кажется с функциями код выглядит более читабельно,
#  нет непонятных подстановок по индексам в функциях ниже,
#  а так как константы все равно нужно было копировать,
#  предполагаю, что памяти расходую примерно одинаково.
#  Сделала на свой страх и риск)


async def spreadsheets_create(
    wrapper_services: Aiogoogle,
) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = create_spreadsheet_body(now_date_time)
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheetid = response['spreadsheetId']
    return spreadsheetid


async def set_user_permissions(
        spreadsheetid: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheetid: str,
        projects: List[CharityProjectDB],
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_head = creat_table_head(now_date_time)
    sorted_projects = sorted(((
        project.name, project.close_date - project.create_date, project.description
    ) for project in projects), key=itemgetter(1))
    table_values = [
        *table_head,
        *[list(map(str, project)) for project in sorted_projects],
    ]
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    if len(table_values) > ROWS:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=TABLE_SIZE_ERROR.format(ROWS),
        )
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range=f'R1C1:R{len(table_values)}C3',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
