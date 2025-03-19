from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.help_dialog.getters import start_getter

from states.state_groups import helpSG


help_dialog = Dialog(
    Window(
        Format('{text}'),
        Column(
            Url(Format('{contact}'), id='contact_button', url=Const('https://t.me/SR_support_me')),
        ),
        getter=start_getter,
        state=helpSG.start
    ),

)