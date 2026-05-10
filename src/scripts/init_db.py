from pathlib import Path
import sqlite3


def main() -> None:
    base = Path("/app/data")
    base.mkdir(parents=True, exist_ok=True)
    schema_dir = Path("/app/infra/sql")

    targets = {
        "source_connector.db": ["ingestion_tables.sql"],
        "batch_ingestion.db": ["ingestion_tables.sql"],
        "streaming_ingestion.db": ["ingestion_tables.sql"],
        "document_parsing.db": ["ingestion_tables.sql"],
        "semantic_normalization.db": ["normalized_tables.sql"],
        "entity_resolution.db": ["entity_tables.sql"],
        "feature_engineering.db": ["feature_store_tables.sql"],
        "knowledge_graph.db": ["graph_relations.sql"],
    }

    for db_name, scripts in targets.items():
        connection = sqlite3.connect(base / db_name)
        try:
            for script_name in scripts:
                connection.executescript((schema_dir / script_name).read_text(encoding="utf-8"))
            connection.commit()
        finally:
            connection.close()


if __name__ == "__main__":
    main()
