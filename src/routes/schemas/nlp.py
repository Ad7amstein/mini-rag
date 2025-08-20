import os
from typing import Optional
from pydantic import BaseModel


class PushRequest(BaseModel):
    do_reset: Optional[int] = 0


class SearchRequest(BaseModel):
    text: str
    limit: Optional[int] = 5


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
