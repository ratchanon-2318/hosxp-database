import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from rich.console import Console
from rich.table import Table
from rich import box

connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="",
    host="127.0.0.1",
    port=3306,
    database="hos",
)

engine = create_engine(connection_url)
console = Console()

try:
    df = pd.read_sql("DESCRIBE patient", engine)

    table = Table(
        title="โครงสร้างตาราง PATIENT",
        box=box.SQUARE,
        show_lines=True,
    )

    for col in df.columns:
        table.add_column(col, overflow="fold")

    for row in df.itertuples(index=False):
        table.add_row(*[str(v) for v in row])

    console.print(table)
    console.print(f"\nจำนวนคอลัมน์ทั้งหมด: {len(df)}")

except Exception as e:
    console.print(f"[red]เกิดข้อผิดพลาด:[/red] {e}")

finally:
    engine.dispose()
