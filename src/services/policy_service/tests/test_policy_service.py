from services.common.models import PolicyRequest
from services.common.storage import SqliteStore
from services.policy_service.core import PolicyService


def test_policy_violation(tmp_path):
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
        ("tenant-a", "ent-1", "cloud_cost", "v1", 12.0, "2026-05-09T00:00:00Z"),
    )
    service = PolicyService(store)
    result = service.evaluate(PolicyRequest(tenant_id="tenant-a", constraints={"cloud_cost": 10.0}))
    assert result.allowed is False

