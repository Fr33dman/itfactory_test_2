import io

from openpyxl.workbook.workbook import Workbook
from openpyxl import load_workbook


def read_file(file: io.BytesIO) -> list:
    workbook = load_workbook(filename=file)
    result = workbook_2_list(workbook)
    return result


def workbook_2_list(workbook: Workbook) -> list:
    """
    Формат:

    [ - список листов в документе
        { - словарь одного листа
            'titles': [ - колонки
                'a',
                'b',
                'c',
                ...
            ],
            'rows': [ - строки
                [1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10],
                ...
            ]
        },
        ...
    ]
    """
    result = []
    # Да, это можно было сделать через классы, но мне было довольно лень + если бы тут закладывался
    # конечно более сложный функционал, то имело бы смысл делать нормальную систему через датафреймы

    for sheet in workbook.worksheets:
        dict_sheet = {
            'titles': [],
            'rows': [],
        }

        titles = list(sheet.values)[0]
        dict_sheet['titles'] = list(filter(lambda x: x is not None, titles))

        for row in list(sheet.values)[1:]:
            dict_sheet['rows'].append(list(filter(lambda x: x is not None, list(row))))

        result.append(dict_sheet)

    return result
