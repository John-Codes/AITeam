import os
import json
import re
from pathlib import Path
from hashids import Hashids
from Server_Config.Server_Side.models import ChatInfo, Product, Keyword, ListItem
hashids = Hashids(salt = os.getenv("salt"), min_length=8)

class DataSaver:

    def __init__(self):
        # Definimos la ruta base para todos los archivos que manejaremos
        self.base_path = Path(__file__).parent / "memory_text"
    
    def format_str_to_dict(self, json_str):
        # Primero, extraemos el contenido entre las llaves
        match = re.search(r'{.*}', json_str, re.DOTALL)
        if not match:
            print('no match a dict')

        # Luego, convertimos el string limpio a un diccionario
        try:
            clean_json_str = match.group(0)
            data_dict = json.loads(clean_json_str)
            print('json generated')
            return data_dict
        except Exception as e:
            print('not json generated')
            print(e)

    
    def create_or_update_page(self, user_id, user_json_page):
        data_dict = self.format_str_to_dict(user_json_page)
        if self.check_if_user_data_exists(user_id):
            self.update_user_data(user_id, data_dict)
        else:
            self.create_new_user_data(user_id, data_dict)

    def check_if_user_data_exists(self, user_id):
        # Comprueba si el usuario ya tiene información guardada
        return ChatInfo.objects.filter(id=user_id).exists()

    def create_new_user_data(self, user_id, data_dict):
        # Crea nuevos registros en la base de datos
        general_info = ChatInfo(
            id=user_id,
            title=data_dict.get('title'),
            header=data_dict.get('header'),
            description=data_dict.get('description'),
            default_message=data_dict.get('default_message')
        )
        general_info.save()

        for keyword in data_dict.get('keywords', []):
            Keyword.objects.create(general_info=general_info, keyword=keyword)

        for item in data_dict.get('list_items', []):
            ListItem.objects.create(
                general_info=general_info,
                text=item['text'],
                url=item['url']
            )

        for product in data_dict.get('products', []):
            Product.objects.create(
                general_info=general_info,
                name=product['name'],
                description=product['description'],
                value=product['value'],
                url=product['url']
            )

def update_user_data(self, user_id, data_dict):
    # Obtener el objeto GeneralInfo/ChatInfo existente
    general_info = ChatInfo.objects.get(id=user_id)

    # Actualizar los campos básicos
    general_info.title = data_dict.get('title', general_info.title)
    general_info.header = data_dict.get('header', general_info.header)
    general_info.description = data_dict.get('description', general_info.description)
    general_info.default_message = data_dict.get('default_message', general_info.default_message)
    general_info.save()

    # Actualizar Keywords
    self.update_keywords(general_info, data_dict)

    # Actualizar ListItems
    self.update_list_items(general_info, data_dict)

    # Actualizar Products
    self.update_products(general_info, data_dict)

def update_keywords(self, general_info, data_dict):
    new_keywords = set(data_dict.get('keywords', []))
    existing_keywords = {kw.keyword for kw in general_info.keywords.all()}

    # Crear nuevos y eliminar los que ya no están
    for keyword in new_keywords - existing_keywords:
        Keyword.objects.create(general_info=general_info, keyword=keyword)

    for keyword in existing_keywords - new_keywords:
        Keyword.objects.filter(general_info=general_info, keyword=keyword).delete()

def update_list_items(self, general_info, data_dict):
    new_items = {item['text']: item for item in data_dict.get('list_items', [])}
    existing_items = {li.text: li for li in general_info.list_items.all()}

    for text, item in new_items.items():
        if text in existing_items:
            existing_item = existing_items[text]
            existing_item.url = item['url']
            existing_item.save()
        else:
            ListItem.objects.create(general_info=general_info, text=item['text'], url=item['url'])

    for text in existing_items:
        if text not in new_items:
            ListItem.objects.filter(general_info=general_info, text=text).delete()

def update_products(self, general_info, data_dict):
    new_products = {product['name']: product for product in data_dict.get('products', [])}
    existing_products = {prod.name: prod for prod in general_info.products.all()}

    for name, product in new_products.items():
        if name in existing_products:
            existing_product = existing_products[name]
            existing_product.description = product['description']
            existing_product.value = product['value']
            existing_product.url = product['url']
            existing_product.save()
        else:
            Product.objects.create(
                general_info=general_info,
                name=product['name'],
                description=product['description'],
                value=product['value'],
                url=product['url']
            )

    for name in existing_products:
        if name not in new_products:
            Product.objects.filter(general_info=general_info, name=name).delete()
