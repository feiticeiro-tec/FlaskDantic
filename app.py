from flask import Flask
from flask_dantic import FDantic
from flask_restx import Resource
from pydantic import BaseModel, validator


DB = {}


def validate_cnpj(cnpj: str) -> bool:
    if "0" in cnpj:
        raise ValueError("CNPJ Inválido")
    return cnpj


class Endereco(BaseModel):
    id: int
    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str
    complemento: str | None = None

    def add(self):
        DB.setdefault("endereco", [])
        DB["endereco"].append(
            {
                "id": self.id,
                "rua": self.rua,
                "numero": self.numero,
                "bairro": self.bairro,
                "cidade": self.cidade,
                "estado": self.estado,
                "cep": self.cep,
                "complemento": self.complemento,
            }
        )


class Cliente(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    enderecos: list[Endereco] | None = None

    def add(self):
        DB.setdefault("cliente", [])
        DB["cliente"].append(
            {
                "id": self.id,
                "nome": self.nome,
                "email": self.email,
                "telefone": self.telefone,
            }
        )


class Empresa(BaseModel):
    id: int
    nome: str
    cnpj: str
    enderecos: list[Endereco] | None = None
    clientes: list[Cliente] | None = None

    def add(self):
        DB.setdefault("empresa", [])
        DB["empresa"].append(
            {
                "id": self.id,
                "nome": self.nome,
                "cnpj": self.cnpj,
            }
        )

    @validator("cnpj")
    def _validate_cnpj(cls, cnpj: str):
        return validate_cnpj(cnpj=cnpj)


class Usuario(BaseModel):
    id: int
    username: str
    password: str
    empresas: list[Empresa] | None = None

    def add(self):
        DB.setdefault("usuario", [])
        DB["usuario"].append(
            {
                "id": self.id,
                "username": self.username,
                "password": self.password,
            }
        )


app = Flask(__name__)
api = FDantic(app)

np = api.namespace("grupo")
np.model_pydantic(Endereco)
np.model_pydantic(Cliente)
np.model_pydantic(Empresa)
user = np.model_pydantic(Usuario)


class UsuarioResource(Resource):
    @user.validate(np)
    def post(self):
        data: Usuario = self.payload
        data.add()
        for empresa in data.empresas:
            empresa.add()
            for cliente in empresa.clientes:
                cliente.add()
                for endereco in cliente.enderecos:
                    endereco.add()
        return DB


np.add_resource(UsuarioResource, "/")
