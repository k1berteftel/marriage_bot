from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Cancel
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.admin_dialog import getters
from states.state_groups import adminSG, targetingSG

admin_dialog = Dialog(
    Window(
        Const('Админ панель'),
        Button(Const('📊 Получить статистику'), id='get_static', on_click=getters.get_static),
        SwitchTo(Const('Выдать вип'), id='set_vip_switcher', state=adminSG.set_vip),
        Button(Const('Получить статистику по рефералам'), id='get_refs_static', on_click=getters.get_refs_static),
        SwitchTo(Const('Работа с жалобами'), id='complain_menu', state=adminSG.complain_menu),
        SwitchTo(Const('Заблокировать пользователя'), id='block_user_switcher', state=adminSG.block_user),
        SwitchTo(Const('Таргетированный показы'), id='target_menu_switcher', state=adminSG.target_menu),
        SwitchTo(Const('Сделать рассылку'), id='mailing_menu_switcher', state=adminSG.mailing_menu),
        SwitchTo(Const('Управление ОП'), id='op_menu_switcher', state=adminSG.op_menu),
        SwitchTo(Const('Управление тарифами'), id='rate_menu_switcher', state=adminSG.rate_menu),
        SwitchTo(Const('🔗 Управление диплинками'), id='deeplinks_menu_switcher', state=adminSG.deeplink_menu),
        SwitchTo(Const('👥 Управление админами'), id='admin_menu_switcher', state=adminSG.admin_menu),
        Button(Const('Выгрузка базы пользователей'), id='get_users_txt', on_click=getters.get_users_txt),
        Cancel(Const('Назад'), id='close_admin'),
        state=adminSG.start
    ),
    Window(
        Const('Введите username или user_id пользователя которого надо заблокировать'),
        TextInput(
            id='get_block_user',
            on_success=getters.get_block_user
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        state=adminSG.block_user
    ),
    Window(
        Const('Введите ID пользователя которому вы хотели бы выдать бесконечный вип'),
        TextInput(
            id='set_vip',
            on_success=getters.set_vip
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        state=adminSG.set_vip
    ),
    Window(
        Const('Выберите тип рассылки'),
        Column(
            SwitchTo(Const('Обычная рассылка'), id='basic_malling_switcher', state=adminSG.get_mail),
            Start(Const('Таргетированная рассылка'), id='targeting_malling_start', state=targetingSG.menu),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        state=adminSG.mailing_menu
    ),
    Window(
        Const('Тут вы можете управлять системой таргетированных показов и '
              'просматривать статистику этих показов'),
        Column(
            SwitchTo(Const('Создать показ'), id='create_impression_menu_switcher',
                     state=adminSG.create_impression_menu),
            SwitchTo(Const('Просмотр статистики показов'), id='choose_impression_switcher',
                     state=adminSG.choose_impression)
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        state=adminSG.target_menu
    ),
    Window(
        Format('Действующие параметры:\n{params}\nПодходящее кол-во пользователей: {count}'),
        Group(
            SwitchTo(Const('Пол'), id='get_male_switcher', state=adminSG.get_male),
            Button(Const('Сбросить пол'), id='male_throw', on_click=getters.throw_off),
            SwitchTo(Const('Возраст'), id='get_age_range_switcher', state=adminSG.get_age_range),
            Button(Const('Сбросить возраст'), id='age_throw', on_click=getters.throw_off),
            SwitchTo(Const('Город'), id='get_city_switcher', state=adminSG.get_city),
            Button(Const('Сбросить город'), id='city_throw', on_click=getters.throw_off),
            SwitchTo(Const('Профессия'), id='get_profession_switcher', state=adminSG.get_profession),
            Button(Const('Сбросить профессия'), id='profession_throw', on_click=getters.throw_off),
            SwitchTo(Const('Образование'), id='get_education_switcher', state=adminSG.get_education),
            Button(Const('Сбросить образование'), id='education_throw', on_click=getters.throw_off),
            SwitchTo(Const('Доход'), id='get_income_switcher', state=adminSG.get_income),
            Button(Const('Сбросить доход'), id='income_throw', on_click=getters.throw_off),
            SwitchTo(Const('Религия'), id='get_religion_switcher', state=adminSG.get_religion),
            Button(Const('Сбросить религию'), id='religion_throw', on_click=getters.throw_off),
            SwitchTo(Const('Семейное положение'), id='get_family_switcher', state=adminSG.get_family),
            Button(Const('Сбросить семейное положение'), id='family_throw', on_click=getters.throw_off),
            SwitchTo(Const('Кол-во детей'), id='get_children_count_switcher', state=adminSG.get_children_count),
            Button(Const('Сбросить кол-во детей'), id='children_count_throw', on_click=getters.throw_off),
            SwitchTo(Const('Отношение по детям'), id='get_children_switcher', state=adminSG.get_children),
            Button(Const('Сбросить отношение по детям'), id='children_throw', on_click=getters.throw_off),
            width=2
        ),
        Button(Const('Начать показы'), id='get_message_id_switcher', on_click=getters.get_message_id_switcher),
        SwitchTo(Const('Назад'), id='back_target_menu', state=adminSG.target_menu),
        getter=getters.create_impression_menu_getter,
        state=adminSG.create_impression_menu
    ),
    Window(
        Const('Выберите показ который вы хотели бы просмотреть'),
        Group(
            Select(
                Format('{item[0]}'),
                id='impressions_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.impression_selector
            ),
            width=1
        ),
        SwitchTo(Const('Назад'), id='back_target_menu', state=adminSG.target_menu),
        getter=getters.choose_impression_getter,
        state=adminSG.choose_impression
    ),
    Window(
        Format('Параметры показа:\n {params}\n\nСтатистика по показам:\n {static}'),
        Column(
            Button(Const('Удалить показ'), id='del_impression', on_click=getters.del_impression),
        ),
        SwitchTo(Const('Назад'), id='back_choose_impression', state=adminSG.choose_impression),
        getter=getters.impression_menu_getter,
        state=adminSG.impression_menu
    ),
    Window(
        Const('Отправьте сообщение которое должно будет отображаться при показе юзеру'),
        MessageInput(
            func=getters.get_message,
            content_types=ContentType.ANY
        ),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        state=adminSG.get_message_id
    ),
    Window(
        Const('Введите кнопки которые будут крепиться к показываемому сообщению\n'
              'Введите кнопки в формате:\n кнопка1 - ссылка1\nкнопка2 - ссылка2'),
        TextInput(
            id='get_impression_keyboard',
            on_success=getters.get_impression_keyboard
        ),
        Button(Const('Начать показы без кнопок'), id='create_impression_model',
               on_click=getters.create_impression_model),
        SwitchTo(Const('Назад'), id='back_get_message_id', state=adminSG.get_message_id),
        state=adminSG.get_impression_keyboard
    ),
    Window(
        Const('Введите диапозон возрастов вашей целевой аудитории в данном формате \n<em>'
              '20-35</em>'),
        TextInput(
            id='get_age',
            on_success=getters.get_age_range
        ),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        state=adminSG.get_age_range
    ),
    Window(
        Const('Укажите пол'),
        Column(
            Button(Format('{men}Мужчина'), id='men_choose', on_click=getters.choose_male),
            Button(Format('{women}Женщина'), id='women_choose', on_click=getters.choose_male),
        ),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        getter=getters.get_male_getter,
        state=adminSG.get_male
    ),
    Window(
        Const('Введите название города или несколько городов через абзац, '
              'например чтобы добавить несколько городов напишите так:\nМосква\nПитер\nи так далее..'),
        TextInput(
            id='get_city',
            on_success=getters.get_city
        ),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        state=adminSG.get_city
    ),
    Window(
        Const('Введите название профессии или несколько профессий разделенных абзацом, '
              'н-р:\nповар\nкосметолог\nи так далее..'),
        TextInput(
            id='get_profession',
            on_success=getters.get_profession
        ),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        state=adminSG.get_profession
    ),
    Window(
        Const('Укажите уровень образования'),
        Column(
            Button(Format('{leaning}Еще учусь'), id='leaning_education_choose', on_click=getters.choose_education),
            Button(Format('{eleven}11 классов'), id='eleven_education_choose', on_click=getters.choose_education),
            Button(Format('{average}Среднее специальное'), id='average_education_choose', on_click=getters.choose_education),
            Button(Format('{higher}Высшее'), id='higher_education_choose', on_click=getters.choose_education),
        ),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        getter=getters.get_education_getter,
        state=adminSG.get_education
    ),
    Window(
        Const('Укажите уровень дохода'),
        Column(
            Button(Format('{no}Нет дохода'), id='no_income_choose', on_click=getters.choose_income),
            Button(Format('{low}Низкий'), id='low_income_choose', on_click=getters.choose_income),
            Button(Format('{average}Средний'), id='average_income_choose', on_click=getters.choose_income),
            Button(Format('{high}Высокий'), id='high_income_choose', on_click=getters.choose_income),
        ),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        getter=getters.get_income_getter,
        state=adminSG.get_income
    ),
    Window(
        Const('Укажите религию'),
        Column(
            Button(Format('{christian}Христианство'), id='christian_choose', on_click=getters.choose_religion),
            Button(Format('{islam}Ислам'), id='islam_choose', on_click=getters.choose_religion),
            Button(Format('{another}Другое'), id='another_choose', on_click=getters.choose_religion),
        ),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        getter=getters.get_religion_getter,
        state=adminSG.get_religion
    ),
    Window(
        Const('Укажите семейное положение'),
        Column(
            Button(Format('{no}Никогда не был(а) в браке'), id='no_family_choose', on_click=getters.choose_family),
            Button(Format('{divorce}Разведен'), id='divorce_family_choose', on_click=getters.choose_family),
            Button(Format('{widow}Вдовец/вдова'), id='widow_family_choose', on_click=getters.choose_family),
        ),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        getter=getters.get_family_getter,
        state=adminSG.get_family
    ),
    Window(
        Const('Укажите кол-во детей'),
        TextInput(
            id='get_children_count',
            on_success=getters.get_children_count
        ),
        Button(Const('Нет детей'), id='no_children_count_choose', on_click=getters.choose_children_count),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        state=adminSG.get_children_count
    ),
    Window(
        Const('Укажите отношение к заводу детей'),
        Column(
            Button(Format('{yes}Да'), id='yes_children_choose', on_click=getters.choose_children),
            Button(Format('{no}Нет'), id='no_children_choose', on_click=getters.choose_children),
            Button(Format('{maybe}Возможно'), id='maybe_children_choose', on_click=getters.choose_children),
            Button(Format('{not}Не важно'), id='not_matter_children_choose', on_click=getters.choose_children),
        ),
        SwitchTo(Const('Назад'), id='back_create_impression_menu', state=adminSG.create_impression_menu),
        getter=getters.get_children_getter,
        state=adminSG.get_children
    ),
    Window(
        DynamicMedia('media', when='media'),
        Format('{text}\n'),
        Format('<b>Причина жалобы:</b>\n{complain_text}', when='complain'),
        Row(
            Button(Const('<'), id='previous_complain_page', on_click=getters.complain_pager, when='not_first'),
            Button(Const('>'), id='next_complain_page', on_click=getters.complain_pager, when='not_last'),
        ),
        Group(
            Button(Const('Заблокировать юзера'), id='block_user', on_click=getters.block_user, when='complain'),
            SwitchTo(Const('Кинуть предупреждение'), id='send_warning_switcher', state=adminSG.get_warning, when='complain'),
            Button(Const('Игнорировать|Удалить жалобу'), id='del_complain', on_click=getters.del_complain, when='complain'),
            width=2
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.complain_menu_getter,
        state=adminSG.complain_menu
    ),
    Window(
        Const('Отправьте текст предупреждения, он отправится юзеру получившему данную жалобу'),
        TextInput(
            id='get_warning',
            on_success=getters.get_warning
        ),
        SwitchTo(Const('Назад'), id='back_complain_menu', state=adminSG.complain_menu),
        state=adminSG.get_warning
    ),
    Window(
        Format('🔗 *Меню управления диплинками*\n\n'
               '🎯 *Имеющиеся диплинки*:\n{links}'),
        Column(
            Button(Const('➕ Добавить диплинк'), id='add_deeplink', on_click=getters.add_deeplink),
            SwitchTo(Const('❌ Удалить диплинки'), id='del_deeplinks', state=adminSG.deeplink_del),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.deeplink_menu_getter,
        state=adminSG.deeplink_menu
    ),
    Window(
        Const('❌ Выберите диплинк для удаления'),
        Group(
            Select(
                Format('🔗 {item[0]}'),
                id='deeplink_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_deeplink
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='deeplinks_back', state=adminSG.deeplink_menu),
        getter=getters.del_deeplink_getter,
        state=adminSG.deeplink_del
    ),
    Window(
        Format('👥 *Меню управления администраторами*\n\n {admins}'),
        Column(
            SwitchTo(Const('➕ Добавить админа'), id='add_admin_switcher', state=adminSG.admin_add),
            SwitchTo(Const('❌ Удалить админа'), id='del_admin_switcher', state=adminSG.admin_del)
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.admin_menu_getter,
        state=adminSG.admin_menu
    ),
    Window(
        Const('👤 Выберите пользователя, которого хотите сделать админом\n'
              '⚠️ Ссылка одноразовая и предназначена для добавления только одного админа'),
        Column(
            Url(Const('🔗 Добавить админа (ссылка)'), id='add_admin',
                url=Format('http://t.me/share/url?url=https://t.me/SR_znakomstva_bot?start={id}')),  # поменять ссылку
            Button(Const('🔄 Создать новую ссылку'), id='new_link_create', on_click=getters.refresh_url),
            SwitchTo(Const('🔙 Назад'), id='back_admin_menu', state=adminSG.admin_menu)
        ),
        getter=getters.admin_add_getter,
        state=adminSG.admin_add
    ),
    Window(
        Const('❌ Выберите админа для удаления'),
        Group(
            Select(
                Format('👤 {item[0]}'),
                id='admin_del_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_admin
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back_admin_menu', state=adminSG.admin_menu),
        getter=getters.admin_del_getter,
        state=adminSG.admin_del
    ),
    # _____
    Window(
        Const('🔗 Введите свою ссылку на канал или пропустите этот шаг, '
              'чтобы бот сам подобрал ссылку для канала или чата'),
        TextInput(
            id='get_button_link',
            on_success=getters.get_button_link
        ),
        Button(Const('⏭ Пропустить'), id='continue_no_link', on_click=getters.save_without_link),
        state=adminSG.get_button_link
    ),
    Window(
        Format('📋 *Меню управления ОП*\n\n'
               '📋 *Действующие каналы*:\n\n {buttons}\n\n'
               '🔗 *Ссылки*: \n'
               '📺 Канал: {channel_link}\n'
               '💬 Чат: {chat_link}'),
        Column(
            Url(Const('➕ Добавить канал'), id='add_channel', url=Format('{channel_link}')),
            Url(Const('➕ Добавить чат'), id='add_chat', url=Format('{chat_link}')),
        ),
        Group(
            Select(
                Format('💼 {item[0]}'),
                id='buttons_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.op_buttons_switcher
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.op_menu_getter,
        state=adminSG.op_menu
    ),
    Window(
        Format('Канал|Чат {channel_name}\nУказанная ссылка на канал|чат: {channel_link}'),
        SwitchTo(Const('Изменить ссылку на канал'), id='change_button_link_switcher', state=adminSG.change_button_link),
        SwitchTo(Const('Назад'), id='back_op_menu', state=adminSG.op_menu),
        getter=getters.button_menu_getter,
        state=adminSG.button_menu
    ),
    Window(
        Const('🔗 Введите новую ссылку для кнопки\n\n'
              '⚠️ <em>Важно: ссылка должна вести на тот же канал, иначе могут возникнуть проблемы с проверкой ОП</em>'),
        TextInput(
            id='change_button_link',
            on_success=getters.change_button_link
        ),
        state=adminSG.change_button_link
    ),
    #  _______
    Window(
        Format('💵 *Действующие тарифы*:\n\n{rates}'),
        Column(
            SwitchTo(Const('➕ Добавить тариф'), id='add_rate_amount_switcher', state=adminSG.add_rate_amount),
            SwitchTo(Const('✏️ Изменить тарифы'), id='choose_rate_switcher', state=adminSG.choose_rate),
            SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start)
        ),
        getter=getters.rate_menu_getter,
        state=adminSG.rate_menu
    ),
    Window(
        Const('💬 Введите количество токенов для тарифа'),
        TextInput(
            id='get_rate_amount',
            on_success=getters.get_rate_amount
        ),
        SwitchTo(Const('🔙 Назад'), id='back_rate_menu', state=adminSG.rate_menu),
        state=adminSG.add_rate_amount
    ),
    Window(
        Const('💬 Введите цену за указанное количество токенов'),
        TextInput(
            id='get_rate_price',
            on_success=getters.get_rate_price
        ),
        SwitchTo(Const('🔙 Назад'), id='back_rate_menu', state=adminSG.rate_menu),
        state=adminSG.add_rate_price
    ),
    Window(
        Const('🔍 Выберите тариф для изменения'),
        Group(
            Select(
                Format('💼 {item[0]}'),
                id='rate_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.choose_rate
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back_rate_menu', state=adminSG.rate_menu),
        getter=getters.rate_choose_getter,
        state=adminSG.choose_rate
    ),
    Window(
        Format('💼 *Данные выбранного тарифа*:\n\n{rate}'),
        Column(
            SwitchTo(Const('🔄 Изменить количество токенов'), id='change_rate_amount_switcher',
                     state=adminSG.change_rate_amount),
            SwitchTo(Const('💲 Изменить цену'), id='change_rate_price_switcher', state=adminSG.change_rate_price),
            Button(Const('Удалить тариф'), id='del_rate', on_click=getters.del_rate),
        ),
        SwitchTo(Const('🔙 Назад'), id='back_rate_menu', state=adminSG.rate_menu),
        getter=getters.rate_change_getter,
        state=adminSG.change_rate_menu
    ),
    Window(
        Const('💬 Введите количество токенов для изменения'),
        TextInput(
            id='change_rate_amount',
            on_success=getters.change_rate_amount
        ),
        SwitchTo(Const('🔙 Назад'), id='back_change_rate_menu', state=adminSG.change_rate_menu),
        state=adminSG.change_rate_amount
    ),
    Window(
        Const('💬 Введите цену за данное количество токенов'),
        TextInput(
            id='change_gen_rate_price',
            on_success=getters.change_rate_price
        ),
        SwitchTo(Const('🔙 Назад'), id='back_change_rate_menu', state=adminSG.change_rate_menu),
        state=adminSG.change_rate_price
    ),
    Window(
        Const('Введите сообщение которое вы хотели бы разослать'),
        MessageInput(
            content_types=ContentType.ANY,
            func=getters.get_mail
        ),
        SwitchTo(Const('Назад'), id='back', state=adminSG.start),
        state=adminSG.get_mail
    ),
    Window(
        Const('Введите время через которое сообщение должно удалиться у всех пользователей\n'
              'Введите текст в формате: 02:30 (2 часа: 30 минут)'),
        TextInput(
            id='get_time',
            on_success=getters.get_time
        ),
        SwitchTo(Const('Продолжить без автоудаления'), id='get_keyboard_switcher', state=adminSG.get_keyboard),
        SwitchTo(Const('Назад'), id='back_get_mail', state=adminSG.get_mail),
        state=adminSG.get_time
    ),
    Window(
        Const('Введите кнопки которые будут крепиться к рассылаемому сообщению\n'
              'Введите кнопки в формате:\n кнопка1 - ссылка1\nкнопка2 - ссылка2'),
        TextInput(
            id='get_mail_keyboard',
            on_success=getters.get_mail_keyboard
        ),
        SwitchTo(Const('Продолжить без кнопок'), id='confirm_mail_switcher', state=adminSG.confirm_mail),
        SwitchTo(Const('Назад'), id='back_get_time', state=adminSG.get_time),
        state=adminSG.get_keyboard
    ),
    Window(
        Const('Вы подтверждаете рассылку сообщения'),
        Row(
            Button(Const('Да'), id='start_malling', on_click=getters.start_malling),
            Button(Const('Нет'), id='cancel_malling', on_click=getters.cancel_malling),
        ),
        SwitchTo(Const('Назад'), id='back_get_keyboard', state=adminSG.get_keyboard),
        state=adminSG.confirm_mail
    ),
)
