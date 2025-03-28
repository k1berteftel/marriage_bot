from database.action_data_class import DataInteraction
from database.model import FormTable, UsersTable


async def sort_forms(forms: list[int], session: DataInteraction, owner_age: int) -> list[int]:
    place = 0
    for i in range(0, 17):
        for j in range(place, len(forms)):
            form = await session.get_form_by_id(forms[j])
            if form.age in range(owner_age - i, owner_age + i):
                elem = forms.pop(j)
                forms.insert(place, elem)
                place += 1

    n = len(forms)
    for i in range(n):
        for j in range(0, n-i-1):
            first_form = await session.get_form_by_id(forms[j])
            first_user = await session.get_user(first_form.user_id)
            second_form = await session.get_form_by_id(forms[j+1])
            second_user = await session.get_user(second_form.user_id)
            if not first_form.boost and second_form.boost:
                forms[j], forms[j+1] = forms[j+1], forms[j]
                continue
            if first_form.boost:
                continue
            if (first_user.vip and not first_form.photos) and (second_user.vip and second_form.photos):
                forms[j], forms[j+1] = forms[j+1], forms[j]
                continue
            if not first_form.photos and second_form.photos:
                forms[j], forms[j+1] = forms[j+1], forms[j]
                continue
            if not first_user.vip and second_user.vip:
                forms[j], forms[j+1] = forms[j+1], forms[j]
                continue

    return forms