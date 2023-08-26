from flask import Flask
from flask_dantic import FDantic
from flask_restx import Resource
from pydantic import BaseModel


class Usuario(BaseModel):
    id: int
    username: str
    password: str


app = Flask(__name__)
api = FDantic(app)

np = api.namespace("grupo")
user = np.model_pydantic(Usuario)


class UsuarioResource(Resource):
    @user.validate(np)
    def post(self):
        data: Usuario = self.payload
        return data.dict()


np.add_resource(UsuarioResource, "/")
