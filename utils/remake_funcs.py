from database.action_data_class import DataInteraction
from utils.geo import get_geo


async def change_users_location(session: DataInteraction):
    forms = await session.get_forms()
    for form in forms:
        user = await session.get_user(form.user_id)
        if not user.active:
            await session.set_form_active(user.user_id, False)
            continue
        if not form.location:
            try:
                result = await get_geo(form.city, user.locale)
                if not result:
                    continue
            except Exception:
                continue
            await session.update_location(user.user_id, result[0], result[1])