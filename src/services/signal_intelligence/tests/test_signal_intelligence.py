from services.common.storage import SqliteStore
from services.signal_intelligence.core import SignalIntelligenceService


def test_signal_scoring(tmp_path):
    store = SqliteStore(str(tmp_path / "feature.db"))
    store.executescript(
        """
        create table if not exists feature_record (
          feature_id integer primary key autoincrement,
          tenant_id text not null,
          entity_id text not null,
          feature_name text not null,
          feature_version text not null,
          value real not null,
          observed_ts text not null
        );
        """
    )
    store.execute(
        "insert into feature_record (tenant_id, entity_id, feature_name, feature_version, value, observed_ts) values (?, ?, ?, ?, ?, ?)",
        ("tenant-a", "ent-1", "engagement", "v1", 8.0, "2026-05-09T00:00:00Z"),
    )
    service = SignalIntelligenceService(store)
    result = service.score("tenant-a")
    assert result.signals[0].feature_name == "engagement"
    assert result.signals[0].score > 0

