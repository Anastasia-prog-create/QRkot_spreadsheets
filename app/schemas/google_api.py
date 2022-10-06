from pydantic import BaseModel, Field, HttpUrl

URL_EXAMPLE = 'https://docs.google.com/spreadsheets/d/{spreadsheetid}'


class CharityProjectGoogle(BaseModel):
    url: HttpUrl = Field(
        ...,
        example=URL_EXAMPLE
    )
