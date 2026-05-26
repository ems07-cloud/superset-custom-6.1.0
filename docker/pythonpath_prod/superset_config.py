# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# Production-like local config used by docker-compose-prod-local.yml.
# Wires Postgres metadata DB, Redis cache, Celery broker + result backend,
# and async SQL Lab queries.
import logging
import os

from celery.schedules import crontab

logger = logging.getLogger()

DATABASE_DIALECT = os.getenv("DATABASE_DIALECT", "postgresql")
DATABASE_USER = os.getenv("DATABASE_USER", "superset")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "superset")
DATABASE_HOST = os.getenv("DATABASE_HOST", "db")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_DB = os.getenv("DATABASE_DB", "superset")

SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
)

EXAMPLES_USER = os.getenv("EXAMPLES_USER", "examples")
EXAMPLES_PASSWORD = os.getenv("EXAMPLES_PASSWORD", "examples")
EXAMPLES_HOST = os.getenv("EXAMPLES_HOST", "db")
EXAMPLES_PORT = os.getenv("EXAMPLES_PORT", "5432")
EXAMPLES_DB = os.getenv("EXAMPLES_DB", "examples")

SQLALCHEMY_EXAMPLES_URI = (
    f"{DATABASE_DIALECT}://"
    f"{EXAMPLES_USER}:{EXAMPLES_PASSWORD}@"
    f"{EXAMPLES_HOST}:{EXAMPLES_PORT}/{EXAMPLES_DB}"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_CACHE_DB = os.getenv("REDIS_CACHE_DB", "1")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "2")
REDIS_ASYNC_DB = os.getenv("REDIS_ASYNC_DB", "3")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_CACHE_DB,
}
DATA_CACHE_CONFIG = {**CACHE_CONFIG, "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 24}
FILTER_STATE_CACHE_CONFIG = {**CACHE_CONFIG, "CACHE_KEY_PREFIX": "superset_filter_"}
EXPLORE_FORM_DATA_CACHE_CONFIG = {**CACHE_CONFIG, "CACHE_KEY_PREFIX": "superset_form_"}
THUMBNAIL_CACHE_CONFIG = {**CACHE_CONFIG, "CACHE_KEY_PREFIX": "superset_thumb_"}

from cachelib.redis import RedisCache  # noqa: E402

RESULTS_BACKEND = RedisCache(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    key_prefix="superset_results_",
    db=int(REDIS_RESULTS_DB),
)


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
        "superset.tasks.cache",
    )
    worker_prefetch_multiplier = 1
    task_acks_late = True
    task_annotations = {
        "sql_lab.get_sql_results": {"rate_limit": "100/s"},
    }
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "DASHBOARD_RBAC": True,
    "DATASET_FOLDERS": True,
    "GLOBAL_ASYNC_QUERIES": True,
    "EMBEDDABLE_CHARTS": True,
    "THUMBNAILS": True,
}

GLOBAL_ASYNC_QUERIES_TRANSPORT = "polling"
GLOBAL_ASYNC_QUERIES_REDIS_CONFIG = {
    "port": int(REDIS_PORT),
    "host": REDIS_HOST,
    "password": "",
    "db": int(REDIS_ASYNC_DB),
    "ssl": False,
}
GLOBAL_ASYNC_QUERIES_JWT_SECRET = os.getenv(
    "GLOBAL_ASYNC_QUERIES_JWT_SECRET",
    os.getenv("SUPERSET_SECRET_KEY", "change-me-to-a-long-random-string-32+chars"),
)

SQLLAB_CTAS_NO_LIMIT = True

WEBDRIVER_BASEURL = "http://superset:8088/"
WEBDRIVER_BASEURL_USER_FRIENDLY = os.getenv(
    "WEBDRIVER_BASEURL_USER_FRIENDLY", "http://localhost:8088/"
)

ALERT_REPORTS_NOTIFICATION_DRY_RUN = (
    os.getenv("ALERT_REPORTS_NOTIFICATION_DRY_RUN", "true").lower() == "true"
)

log_level_text = os.getenv("SUPERSET_LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, log_level_text.upper(), logging.INFO)
