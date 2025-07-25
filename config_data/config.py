from dataclasses import dataclass

from environs import Env

'''
    При необходимости конфиг базы данных или других сторонних сервисов
'''


@dataclass
class tg_bot:
    token: str
    admin_ids: list[int]


@dataclass
class DB:
    dns: str


@dataclass
class Payment:
    api_key: str


@dataclass
class NatsConfig:
    servers: list[str]


@dataclass
class Dadata:
    api_key: str
    api_secret: str


@dataclass
class Config:
    bot: tg_bot
    db: DB
    payment: Payment
    nats: NatsConfig
    geolocator: Dadata


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        bot=tg_bot(
            token=env('token'),
            admin_ids=list(map(int, env.list('admins')))
            ),
        db=DB(
            dns=env('dns')
        ),
        payment=Payment(
            api_key=env('payment_key')
        ),
        nats=NatsConfig(
            servers=env.list('nats')
        ),
        geolocator=Dadata(
            api_key=env('dadata_key'),
            api_secret=env('dadata_secret')
        )
    )
