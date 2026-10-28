"""Legacy import script.

This script is kept for backward compatibility only. The application now uses
the new importer pipeline in `finance.importer` with SQLAlchemy models.
Use the Streamlit "Import" page instead.
"""


def main() -> None:
    raise NotImplementedError(
        "Use pages/1_Import.py or finance.importer.import_statement() instead."
    )


if __name__ == "__main__":
    main()