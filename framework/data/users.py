from enum import StrEnum


class User(StrEnum):
    """Sauce Demo accounts. All of them share the password from ``Settings.password``."""

    STANDARD = "standard_user"
    LOCKED_OUT = "locked_out_user"
    PROBLEM = "problem_user"
    PERFORMANCE_GLITCH = "performance_glitch_user"
    ERROR = "error_user"
    VISUAL = "visual_user"


# The user a test logs in as unless it parametrizes ``user``.
DEFAULT_USER = User.STANDARD
