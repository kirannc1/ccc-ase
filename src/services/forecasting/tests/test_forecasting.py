from services.common.models import ForecastRequest
from services.common.storage import SqliteStore
from services.forecasting.core import ForecastingService


def test_forecast_trend(tmp_path):
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
    for index, value in enumerate([1.0, 2.0, 3.0], start=1):
        store.execute(
            "insert into feature_record (tenant_id, entity_id, feature_name, feature_version, value, observed_ts) values (?, ?, ?, ?, ?, ?)",
            ("tenant-a", "ent-1", "usage", "v1", value, f"2026-05-0{index}T00:00:00Z"),
        )
    service = ForecastingService(store)
    result = service.forecast(ForecastRequest(tenant_id="tenant-a", entity_id="ent-1", feature_name="usage", horizon=2))
    assert result.forecast == 5.0

