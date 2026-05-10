from services.anomaly_detection.core import AnomalyDetectionService
from services.common.models import AnomalyRequest
from services.common.storage import SqliteStore


def test_anomaly_detection(tmp_path):
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
    for value in [10.0, 11.0, 9.0]:
        store.execute(
            "insert into feature_record (tenant_id, entity_id, feature_name, feature_version, value, observed_ts) values (?, ?, ?, ?, ?, ?)",
            ("tenant-a", "ent-1", "cost", "v1", value, "2026-05-09T00:00:00Z"),
        )
    service = AnomalyDetectionService(store)
    result = service.detect(AnomalyRequest(tenant_id="tenant-a", feature_name="cost", value=25.0, threshold=2.0))
    assert result.anomaly is True

