import json
import logging
import sys

import pendulum

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

log = logging.getLogger(__name__)


@dag(
    schedule_interval="*/5 * * * *",
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=['POSTGRES_TO_POSTGRES'],
)
def etl_dag():
    """
    ### TaskFlow API Tutorial Documentation
    This is a simple ETL data pipeline example which demonstrates the use of
    the TaskFlow API using three simple tasks for Extract, Transform, and Load.
    Documentation that goes along with the Airflow TaskFlow API tutorial is
    located
    [here](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html)
    """

    @task()
    def pre_extract():
        log.info("Pre-extract data process")
        hook = PostgresHook(postgres_conn_id='target_db', schema='target')
        last_id = hook.get_first(
            sql="""
                SELECT MAX(id)
                FROM sale
                """,
            parameters=("BATCH_INTERVAL", "POSTGRES_TO_POSTGRES", "SUCCESS"))
        if last_id[0] is None:
            return {"last_id": None}
        return {"last_id": int(last_id[0])}

    @task()
    def extract(last_id):
        """
        #### Extract task
        A simple Extract task to get data ready for the rest of the data
        pipeline. In this case, getting data is from source db Postgres connection
        """
        log.info(f"Extract data from Postgres conn source_db " + json.dumps(last_id))
        batch_size = 10
        hook = PostgresHook(postgres_conn_id='source_db', schema='source')
        sql_query = f"""
        SELECT id, to_char(creation_date, 'YYYY-MM-DD') as creation_date, sale_value
        FROM sale
        filter_last_id
        LIMIT {batch_size};
        """
        filter_query = ""
        if last_id["last_id"] is not None:
            filter_query = f"WHERE id > {last_id['last_id']}"
        sql_query = sql_query.replace("filter_last_id", filter_query)
        log.info(sql_query)
        records = hook.get_records(sql_query)
        extract_data = [{"id": item[0], "creation_date": item[1], "sale_value": item[2]} for item in records]
        log.info(json.dumps(extract_data))
        return extract_data

    @task()
    def transform(extract_data):
        """
        #### Transform task
        """
        log.info("Transform data")
        return {"transform_data": extract_data}

    # [END transform]

    # [START load]
    @task()
    def load(transform_data):
        """
        #### Load task
        A simple Load task which takes in the result of the Transform task and
        loading the data to target Postgres database
        """
        log.info("Load data from Postgres source_db conn DB to Postgres target_db conn DB")
        status = "SUCCESS"
        start_time = pendulum.now()
        trans_data = transform_data['transform_data']
        length_obj = len(trans_data)
        last_id = None
        try:
            if length_obj > 0:
                hook = PostgresHook(postgres_conn_id='target_db', schema='target')
                sql_insert_bulk = """
                    INSERT INTO sale (id, creation_date, sale_value) VALUES
                """
                values = []
                for item in trans_data:
                    value = f"({item['id']}, '{item['creation_date']}', {item['sale_value']})"
                    values.append(value)
                sql_insert_bulk = sql_insert_bulk + ",\n".join(values) + ';'
                hook.run(sql=sql_insert_bulk, autocommit=True)
                last_id = max(item["id"] for item in trans_data)
                error_log = f"Load success {length_obj} records"
            else:
                error_log = "No records found to load"
        except:
            log.error(sys.exc_info()[0])
            status, error_log = "ERROR", str(sys.exc_info()[0])
        finally:
            end_time = pendulum.now()

        return {"after_load_data": {"status": status,
                                    "job_type": "BATCH_INTERVAL",
                                    "job_name": "POSTGRES_TO_POSTGRES",
                                    "job_description": "Transfer data from postgres X to postgres Y",
                                    "batch_size": length_obj,
                                    "last_id": last_id,
                                    "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S'),
                                    "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S'),
                                    "error": error_log
                                    }}

    @task()
    def after_load(after_load_data):
        """
        after_load function is designing to store the job metadata
        """
        log.info(f"Info after load {json.dumps(after_load_data)}")
        hook = PostgresHook(postgres_conn_id='target_db', schema='target')
        after_data = after_load_data["after_load_data"]
        sql_insert_job = f"""
                INSERT INTO job (job_type, job_name, job_description, batch_size, last_id, start_time, end_time, status, error_log)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        hook.run(sql=sql_insert_job,
                 parameters=(
                     after_data["job_type"], after_data["job_name"], after_data["job_description"],
                     after_data["batch_size"], after_data["last_id"], after_data["start_time"],
                     after_data["end_time"], after_data["status"], after_data["error"]
                 ))

    last_id_data = pre_extract()
    sale_extract_data = extract(last_id_data)
    sale_transform_data = transform(sale_extract_data)
    load_data = load(sale_transform_data)
    after_load(load_data)


postgres_etl = etl_dag()
