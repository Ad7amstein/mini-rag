import os
from string import Template


SYSTEM_PROMPT = Template(
    "\n".join(
        [
            "You are an assistant to generate a response for the user.",
            "You will eb provided by a set of documents associated with the user's query.",
            "You have to generate a response based on the documents provided."
            "Ignore the documents that are not relevant to the user's query",
            "You can apologize to the user if you are not apple to generate a response.",
            "You have to generate a response in the same language as the user's query language.",
            "Be polite and respectful to the user.",
            "Be precise and consice in your response. Avoid unnecessary information.",
        ]
    )
)

DOCUMENT_PROMPT = Template(
    "\n".join(["## Document Number: $doc_num", "### Content: $chunk_text"])
)

FOOTER_PROMPT = Template(
    "\n".join(
        [
            "Based only on the above documents, please generate an answer for the user.",
            "## Question:",
            "$query",
            "",
            "## Answer: ",
        ]
    )
)


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
