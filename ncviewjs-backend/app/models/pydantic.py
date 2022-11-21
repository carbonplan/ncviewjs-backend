from tortoise.contrib.pydantic import pydantic_model_creator

from .tortoise import Store

Store_Pydantic = pydantic_model_creator(Store, name='Store')
