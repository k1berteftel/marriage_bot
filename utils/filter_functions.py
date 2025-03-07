from database.action_data_class import DataInteraction
from database.model import FormTable, UsersTable


async def sort_forms(forms: list[int], session: DataInteraction) -> list[int]:
    n = len(forms)
    for i in range(n):
        for j in range(0, n-i-1):
            first_form = await session.get_form_by_id(forms[j])
            first_user = await session.get_user(first_form.user_id)
            second_form = await session.get_form_by_id(forms[j+1])
            second_user = await session.get_user(second_form.user_id)
            if (
                    (not first_form.boost and second_form.boost) or
                    ((first_user.vip and not first_form.photos) and (second_user.vip and second_form.photos)) or
                    (not first_form.photos and second_form.photos) or
                    (not first_user.vip and second_user.vip)
            ):
                forms[j], forms[j+1] = forms[j+1], forms[j]

    return forms