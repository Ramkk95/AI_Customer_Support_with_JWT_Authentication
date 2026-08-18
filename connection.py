
from sqlalchemy import text,create_engine
from streamlit import cache_resource


def connectio_n():
    server = "DESKTOP-HSTTJ5C"
    database = "tt2"

    engine = create_engine(
        f"mssql+pyodbc://@{server}/{database}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
        "&trusted_connection=yes"
    )
    return engine
