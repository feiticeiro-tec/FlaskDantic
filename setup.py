from setuptools import setup


import os


def listar_subpastas(diretorio):
    subpastas = [diretorio]
    for nome in os.listdir(diretorio):
        caminho = os.path.join(diretorio, nome)
        if os.path.isdir(caminho):
            subpastas.append(caminho)
            subpastas.extend(listar_subpastas(caminho))
    return subpastas


with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name="fdantic",
    version="0.1.0",
    url="https://github.com/feiticeiro-tec/feiticeiro-tec",
    license="BSD3",
    author="Silvio Henrique Cruz Da Silva",
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email="silviohenriquecruzdasilva@gmail.com",
    keywords="Pacote",
    description=(
        "Extenção flask para aumento de agilidade de criação"
        " de formulario para o flask-restx"
        " no processo de criação de projeto."
    ),
    packages=listar_subpastas("flask_dantic"),
    install_requires=["flask", "flask-restx", "pydantic"],
)
