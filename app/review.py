from app.schemas import PaperSummary


EDITABLE_FIELDS = [
    "title",
    "problem",
    "method",
    "dataset",
    "metrics",
    "main_results",
    "limitations",
    "relation_to_my_topic",
]


def print_summary(summary: PaperSummary) -> None:
    """
    Print a paper summary in a readable format.
    """
    print("=" * 80)
    print("PAPER SUMMARY REVIEW")
    print("=" * 80)

    for field in EDITABLE_FIELDS:
        value = getattr(summary, field)
        print(f"\n{field}:")
        print(value)

    print("\n" + "=" * 80)


def review_summary(summary: PaperSummary) -> PaperSummary | None:
    """
    Ask the user to approve, edit, or reject a summary.

    Returns:
        PaperSummary if approved.
        None if rejected.
    """
    current_summary = summary

    while True:
        print_summary(current_summary)

        choice = input(
            "\nChoose an action: [a]pprove, [e]dit, [r]eject: "
        ).strip().lower()

        if choice in {"a", "approve"}:
            return current_summary

        if choice in {"r", "reject"}:
            return None

        if choice in {"e", "edit"}:
            print("\nEditable fields:")
            for field in EDITABLE_FIELDS:
                print(f"- {field}")

            field_name = input("\nWhich field do you want to edit? ").strip()

            if field_name not in EDITABLE_FIELDS:
                print(f"\nUnknown field: {field_name}")
                continue

            new_value = input(f"\nEnter new value for '{field_name}': ").strip()

            if not new_value:
                print("\nEmpty value ignored.")
                continue

            current_summary = current_summary.model_copy(
                update={field_name: new_value}
            )

            print(f"\nUpdated field: {field_name}")
            continue

        print("\nUnknown choice. Please type a, e, or r.")