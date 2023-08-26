from typing import _UnionGenericAlias
from types import GenericAlias, UnionType
from functools import partial
from flask_restx import Model, fields, Namespace, Api
from pydantic._internal._model_construction import ModelMetaclass
from .model import FDanticModel


TYPE_PRIMITIVES = {
    str: fields.String,
    bool: fields.Boolean,
    dict: fields.Raw,
    int: fields.Integer,
    float: fields.Float,
}

TYPE_PASS = (ModelMetaclass,)
TYPE_INDEXS = (UnionType, _UnionGenericAlias)


class FDanticCore:
    def get_field(self, models, field_info, field_name):
        """Gera um campo baseado no tipo do campo"""
        tipo_do_campo = type(field_info)
        response = fields.Raw(
            description=field_name,
        )
        #  Tipos primitivos do python
        if field_info in TYPE_PRIMITIVES:
            response = TYPE_PRIMITIVES[field_info](
                description=field_name,
            )
        # Tipos do proprio criado de model
        elif field_info in TYPE_PASS:
            response = field_info
        # Tipos quem container outros tipos
        elif tipo_do_campo in TYPE_INDEXS:
            response = self.get_field(
                models=models,
                field_info=field_info.__args__[0],
                field_name=field_name,
            )
        # Tipos de lista
        elif tipo_do_campo == GenericAlias:
            if len(field_info.__args__) > 0:
                objeto = field_info.__args__[0]
                if isinstance(objeto, ModelMetaclass):
                    try:
                        objeto = models[objeto.__name__]
                    except KeyError as error:
                        raise ReferenceError(
                            f"Modelo {objeto.__name__} não encontrado!",
                        ) from error
                    response = fields.List(
                        fields.Nested(objeto),
                    )
                response = fields.List(
                    self.get_field(
                        models=models,
                        field_info=objeto,
                        field_name=field_name,
                    )
                )
            else:
                response = fields.List(
                    fields.Raw(
                        description=field_name,
                    )
                )

        return response

    def generate_fields(self, models, pydantic_model):
        """Gera os campos baseado no modelo pydantic"""
        items = pydantic_model.__annotations__.items()
        return {
            field_name: self.get_field(
                models=models,
                field_info=field_info,
                field_name=field_name,
            )
            for field_name, field_info in items
        }

    def model_pydantic(self, pydantic_model) -> FDanticModel:
        """Cria um modelo com base no modelo pydantic"""
        restx_model = {}

        if not self.apis:
            raise ReferenceError("Nem uma instancia de api foi encontrada!")
        models = {}

        for api in self.apis:
            models.update(api.models)

        restx_model = self.generate_fields(models, pydantic_model)

        model: Model = self.model(pydantic_model.__name__, restx_model)
        model.setup = partial(FDanticModel.setup, model)
        model.setup(pydantic_model)
        return model

    def setup(self):
        """Adiciona os metodos de pydantic no namespace"""
        self.get_field = partial(FDanticSpace.get_field, self)
        self.generate_fields = partial(FDanticSpace.generate_fields, self)
        self.model_pydantic = partial(FDanticSpace.model_pydantic, self)


class FDanticSpace(Namespace, FDanticCore):
    ...


class FDantic(Api, FDanticCore):
    def namespace(self, *args, **kw) -> FDanticSpace:
        """Cria um namespace com suporte a pydantic"""
        namespace = super().namespace(*args, **kw)
        FDanticSpace.setup(namespace)
        return namespace
