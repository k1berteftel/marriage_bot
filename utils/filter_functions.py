from database.action_data_class import DataInteraction
from database.model import FormTable, UsersTable


async def sort_forms(forms: list[int], session: DataInteraction) -> list[int]:
    counter = 0
    n = len(forms)
    for i in range(n):
        for j in range(0, n-i-1):
            first_form = await session.get_form_by_id(forms[j+1])
            second_form = await session.get_form_by_id(forms[j])
            if first_form.boost and not second_form.boost:
                forms[j], forms[j+1] = forms[j+1], forms[j]
                counter = j + 1

    n = len(forms[counter::])
    print(n)
    for i in range(n):
        for j in range(0, n-i-1):
            form = await session.get_form_by_id(forms[j])
            first_user = await session.get_user(form.user_id)
            form = await session.get_form_by_id(forms[j+1])
            second_user = await session.get_user(form.user_id)
            if not first_user.vip and second_user.vip:
                forms[j], forms[j+1] = forms[j+1], forms[j]

    return forms