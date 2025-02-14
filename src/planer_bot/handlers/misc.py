from logging import getLogger

from linebot.v3.webhooks import (  # type: ignore
    JoinEvent,
    LeaveEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
    UnfollowEvent,
    UnsendEvent,
)

from planer_bot.config import handler

logger = getLogger("uvicorn.app")


@handler.add(UnsendEvent)
async def hadle_unsend(event: UnsendEvent) -> None:  # type: ignore[no-any-unimported]
    line_identifier: str = event.source.user_id
    logger.info(
        f"UnsendEvent. {line_identifier=}, {event.source.group_id=}, {event.unsend.message_id=}"
    )


@handler.add(UnfollowEvent)
async def handle_unfollow(event: UnfollowEvent) -> None:  # type: ignore[no-any-unimported]
    line_identifier: str = event.source.user_id
    logger.info(f"UnfollowEvent. {line_identifier=}")



@handler.add(JoinEvent)
async def handle_join(event: JoinEvent) -> None:  # type: ignore[no-any-unimported]
    logger.info(f"JoinEvent. {event.source.group_id=}")


@handler.add(LeaveEvent)
async def handle_leave(event: LeaveEvent) -> None:  # type: ignore[no-any-unimported]
    logger.info(f"LeaveEvent. {event.source.group_id=}")


@handler.add(MemberJoinedEvent)
async def handle_member_join(event: MemberJoinedEvent) -> None:  # type: ignore[no-any-unimported]
    logger.info(f"MemverJoinEvent. {event.source.group_id=}")


@handler.add(MemberLeftEvent)
async def handle_member_left(event: MemberLeftEvent) -> None:  # type: ignore[no-any-unimported]
    logger.info(f"MemverLeftEvent. {event.source.group_id=}")
