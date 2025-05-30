from asyncio import Future

approval_futures = {}


async def wait_for_approval(chat_id: str) -> dict:
    future = Future()
    approval_futures[chat_id] = future
    return await future


def resolve_approval(chat_id: str, data: dict):
    if chat_id in approval_futures:
        approval_futures[chat_id].set_result(data)
        del approval_futures[chat_id]
