from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Estacao(Base):
    __tablename__ = "estacoes"

    id = Column(Integer, primary_key=True, index=True)
    codigo_estacao = Column(String, unique=True, index=True)
    cidade = Column(String)
    estado = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    # Relacionamento (Uma estação tem várias medições)
    medicoes = relationship("Medicao", back_populates="estacao")


class Medicao(Base):
    __tablename__ = "medicoes"

    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacoes.id"))
    data_medicao = Column(Date)

    # Features (Dados de entrada)
    temperatura_max = Column(Float)
    temperatura_min = Column(Float)
    umidade_relativa = Column(Float)
    pressao_atmosferica = Column(Float)
    velocidade_vento = Column(Float)

    # Target (O que queremos prever)
    choveu_dia_seguinte = Column(Integer)

    # Relacionamento reverso
    estacao = relationship("Estacao", back_populates="medicoes")
