import logging

from typing import Literal

from src.models.enums import ProgramInstruction


def get_instructions(
    close_windows_condition: bool,
    both_windows_condition: bool,
    left_window_status: Literal["open", "closed"],
    right_window_status: Literal["open", "closed"],
    logger: logging.Logger,
) -> list[ProgramInstruction]:

    if close_windows_condition:
        # Close both windows (too cold inside)
        if left_window_status == right_window_status == "closed":
            logger.info("All good, too cold and windows closed.")
            return [ProgramInstruction.NO_OPERATION]

        if left_window_status == right_window_status == "open":
            logger.warning("Too cold and both windows open, closing...")
            return [ProgramInstruction.CLOSE_BOTH]

        if left_window_status == "open":
            # only left open
            logger.warning("Too cold and left window open, closing...")
            return [ProgramInstruction.CLOSE_LEFT]

        logger.warning("Too cold and right window open, closing...")
        return [ProgramInstruction.CLOSE_RIGHT]
    elif both_windows_condition:
        # Open both windows (too hot inside)
        if left_window_status == right_window_status == "open":
            logger.info("All good, Too hot and both windows open.")
            return [ProgramInstruction.NO_OPERATION]

        if left_window_status == right_window_status == "closed":
            logger.warning("Too hot and windows closed, opening...")
            return [ProgramInstruction.OPEN_BOTH]

        if right_window_status == "closed":
            # only right closed
            logger.warning("Too hot and right window closed, opening...")
            return [ProgramInstruction.OPEN_RIGHT]

        logger.warning("Too hot and left window closed, opening...")
        return [ProgramInstruction.OPEN_LEFT]
    else:
        # "Mid-Hot" - Open only left window
        if left_window_status == right_window_status == "open":
            logger.warning("Close right window...")
            return [ProgramInstruction.CLOSE_RIGHT]

        if left_window_status == right_window_status == "closed":
            logger.warning("Open left window...")
            return [ProgramInstruction.OPEN_LEFT]

        if left_window_status == "closed" and right_window_status == "open":
            logger.warning("Open left window and close right...")
            return [
                ProgramInstruction.OPEN_LEFT,
                ProgramInstruction.CLOSE_RIGHT,
            ]

        logger.info("All good, slightly hot and left window open.")
        return [ProgramInstruction.NO_OPERATION]
