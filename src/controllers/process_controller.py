import os
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from controllers.base_controller import BaseController
from controllers import ProjectController
from models import ProcessingEnum


class ProcessController(BaseController):
    def __init__(self, project_id: str) -> None:
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(self.project_id)

    def get_file_extension(self, file_name: str):
        return os.path.splitext(file_name)[-1]

    def get_file_loader(self, file_name: str):
        file_ext = self.get_file_extension(file_name)
        file_path = os.path.join(self.project_path, file_name)
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)

        return None

    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id)
        return loader.load() if loader is not None else None

    def process_file_content(
        self,
        file_content: list,
        file_id: str,
        chunk_size: int = 100,
        overlap_size: int = 20,
    ):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap_size, length_function=len
        )

        file_content_text = [rec.page_content for rec in file_content]
        file_metadata = [rec.metadata for rec in file_content]

        chuncks = text_splitter.create_documents(
            texts=file_content_text, metadatas=file_metadata
        )
        return chuncks


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
