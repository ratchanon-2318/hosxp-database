from flask import Flask, render_template_string, abort
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL

app = Flask(__name__)

# Database Connection
connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="",
    host="127.0.0.1",
    port=3306,
    database="hos",
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True
)

# HTML Template
HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<title>HOSxP Database Explorer</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f1f5f9;
    color: #334155;
}
.header {
    background: #1e293b;
    color: white;
    padding: 17px 24px;
    font-size: 20px;
    font-weight: bold;
}
.layout {
    display: flex;
    min-height: calc(100vh - 58px);
}
.sidebar {
    width: 260px;
    background: white;
    border-right: 1px solid #ddd;
    padding: 18px;
    flex-shrink: 0;
}
.sidebar h3 { margin-top: 0; }
.search {
    width: 100%;
    padding: 10px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    margin-bottom: 15px;
}
.table-link {
    display: block;
    padding: 9px 10px;
    color: #334155;
    text-decoration: none;
    border-radius: 5px;
    font-size: 14px;
}
.table-link:hover, .active {
    background: #dbeafe;
    color: #1d4ed8;
}
.main {
    flex: 1;
    padding: 28px;
    min-width: 0;
}
.card {
    background: white;
    border-radius: 9px;
    padding: 22px;
    box-shadow: 0 1px 4px #00000010;
}
h2 { margin-top: 0; }
.info {
    color: #64748b;
    margin-bottom: 20px;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}
th {
    background: #e2e8f0;
    text-align: left;
}
th, td {
    padding: 12px;
    border: 1px solid #e2e8f0;
}
tr:hover { background: #f8fafc; }
.key {
    color: #2563eb;
    font-weight: bold;
}
.badge {
    display: inline-block;
    background: #dcfce7;
    color: #166534;
    padding: 5px 9px;
    border-radius: 20px;
    font-size: 12px;
}
@media(max-width:700px) {
    .layout { flex-direction: column; }
    .sidebar { width: 100%; }
    .main { padding: 12px; overflow-x: auto; }
}
</style>
</head>

<body>
<div class="header">
    HOSxP Database Explorer
</div>

<div class="layout">
    <aside class="sidebar">
        <h3>Database: hos</h3>
        <input class="search" id="search"
               placeholder="ค้นหาตาราง...">

        <div id="tableList">
        {% for name in tables %}
            <a class="table-link {% if name == selected %}active{% endif %}"
               href="/table/{{ name }}">
               ▦ {{ name }}
            </a>
        {% endfor %}
        </div>
        <p class="info">ทั้งหมด {{ tables|length }} ตาราง</p>
    </aside>

    <main class="main">
        <div class="card">
        {% if selected %}
            <h2>▦ {{ selected }}</h2>
            <div class="info">
                โครงสร้างตาราง
                <span class="badge">
                    {{ columns|length }} Columns
                </span>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Field</th>
                        <th>Type</th>
                        <th>Null</th>
                        <th>Key</th>
                        <th>Default</th>
                        <th>Extra</th>
                    </tr>
                </thead>
                <tbody>
                {% for col in columns %}
                    <tr>
                        <td><b>{{ col.name }}</b></td>
                        <td>{{ col.type }}</td>
                        <td>{{ 'YES' if col.nullable else 'NO' }}</td>
                        <td class="key">
                            {{ 'PRI' if col.primary_key else '' }}
                        </td>
                        <td>{{ col.default if col.default is not none else 'NULL' }}</td>
                        <td>{{ col.autoincrement if col.autoincrement else '' }}</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        {% else %}
            <h2>ยินดีต้อนรับ</h2>
            <p>เลือกตารางจากเมนูด้านซ้ายเพื่อดูโครงสร้าง</p>
            <p class="info">
                HOSxP Database Explorer - Read Only
            </p>
        {% endif %}
        </div>
    </main>
</div>

<script>
document.getElementById("search").addEventListener("input", function() {
    let keyword = this.value.toLowerCase();
    document.querySelectorAll(".table-link").forEach(function(item) {
        item.style.display =
            item.textContent.toLowerCase().includes(keyword)
            ? "block" : "none";
    });
});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())

    return render_template_string(
        HTML,
        tables=tables,
        selected=None,
        columns=[]
    )

@app.route("/table/<table_name>")
def show_table(table_name):
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())

    # ป้องกันการเรียกชื่อตารางที่ไม่มีอยู่จริง
    if table_name not in tables:
        abort(404)

    columns = inspector.get_columns(table_name)
    primary_keys = inspector.get_pk_constraint(table_name)
    pk_columns = primary_keys.get("constrained_columns") or []

    for col in columns:
        col["primary_key"] = col["name"] in pk_columns

    return render_template_string(
        HTML,
        tables=tables,
        selected=table_name,
        columns=columns
    )

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
