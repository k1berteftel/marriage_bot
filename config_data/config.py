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
class Yandex:
    api_key: str


@dataclass
class Config:
    bot: tg_bot
    db: DB
    payment: Payment
    nats: NatsConfig
    yandex: Yandex


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
        yandex=Yandex(
            api_key=env('yandex_key')
        )
    )
