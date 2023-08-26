import json
from functools import partial, wraps
from flask_restx import Model, abort


class FDanticModel(Model):
    @staticmethod
    def validate(namespace):
        """Valida o payload com base no modelo pydantic.

        $ref -> validate_model"""
        return lambda function: function

    @staticmethod
    def _abort_payload(error):
        """Aborta a requisição com o erro de payload"""
        try:
            errors = error.errors()
        except Exception:
            abort(code=500, message="Erro Desconhecido!")
        abort(
            code=400,
            message="Payload Invalido!",
            errors=json.loads(
                json.dumps(errors, default=lambda x: x.__dict__),
            ),
        )

    def _captura_payload(self, model, resource):
        """Captura o payload e tenta converter para o modelo"""

        try:
            resource.payload = model(**resource.api.payload)
        except Exception as error:
            self._abort_payload(error)

    def _validate_model(self, model):
        """Decorador de validação de payload"""

        def capture_namespace(namespace):
            def validate(function):
                @wraps(function)
                # Coloca o modelo como experado
                @namespace.expect(self)
                def wrapper(resource, *args, **kw):
                    # Captura o payload
                    self._captura_payload(model, resource)
                    return function(resource, *args, **kw)

                return wrapper

            return validate

        return capture_namespace

    @classmethod
    def setup(cls, self, model):
        """Adiciona os metodos de pydantic no modelo"""
        self._abort_payload = cls._abort_payload
        self._captura_payload = partial(cls._captura_payload, self)
        self._validate_model = partial(cls._validate_model, self)
        self.validate = self._validate_model(
            model,
        )
        return self._validate_model(model)
