from copy import deepcopy
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
TABLE_SIZE_ERROR = 'Максимальный размер таблицы: {} строк {} столбцов.'

SPREADSHEET_BODY = dict(
    properties=dict(
        title='',
        locale='ru_RU',
    ),
    sheets=[dict(
        properties=dict(
            sheetType='GRID',
            sheetId=0,
            title='Лист1',
            gridProperties=dict(
                rowCount=ROWS,
                columnCount=COLUMNS,
            )
        )
    )]
)

TABLE_HEAD = [
    ['Отчет от', ''],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]


async def spreadsheets_create(
    wrapper_services: Aiogoogle,
    spreadsheet_body=None,
) -> str:
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = (
        deepcopy(SPREADSHEET_BODY) if spreadsheet_body is None
        else spreadsheet_body
    )
    spreadsheet_body['properties']['title'] = (
        f'Отчет на {datetime.now().strftime(FORMAT)}'
    )
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: List[CharityProjectDB],
        wrapper_services: Aiogoogle,
        table_head=None,
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    table_head = (
        deepcopy(TABLE_HEAD) if table_head is None
        else table_head
    )
    table_head[0][1] = datetime.now().strftime(FORMAT)
    sorted_projects = sorted(((
        project.name, project.close_date - project.create_date, project.description
    ) for project in projects), key=itemgetter(1))
    project_columns_count = len(sorted_projects[0])
    table_values = [
        *table_head,
        *[list(map(str, project)) for project in sorted_projects],
    ]
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    if (len(table_values) > ROWS or project_columns_count > COLUMNS):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=TABLE_SIZE_ERROR.format(ROWS, COLUMNS),
        )
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{len(table_values)}C{project_columns_count}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
