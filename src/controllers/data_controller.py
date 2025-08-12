import os
from fastapi import UploadFile
from controllers.base_controller import BaseController


class DataController(BaseController):
    def __init__(self) -> None:
        super().__init__()
        self.size_scale = 1024 * 1024

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.file_allowed_types:
            return False, "File type not supported"
        if file.size > self.app_settings.file_max_size * self.size_scale:  # type: ignore
            return False, "File size exceeded"

        return True, "Upload Sucessful"


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
