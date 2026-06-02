from pydantic import BaseModel, Field


class PaperSummary(BaseModel):
    source_file: str = Field(
        default="",
        description="Path or filename of the source paper PDF",
    )
    title: str = Field(description="Title of the paper")
    problem: str = Field(description="Main problem the paper addresses")
    method: str = Field(description="Main method or approach proposed")
    dataset: str = Field(description="Datasets or experimental settings used")
    metrics: str = Field(description="Evaluation metrics used in the paper")
    main_results: str = Field(description="Main results or findings")
    limitations: str = Field(description="Limitations mentioned or implied")
    relation_to_my_topic: str = Field(
        description="How this paper relates to the user's research topic"
    )