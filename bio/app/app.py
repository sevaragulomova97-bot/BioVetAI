"""BIO-LAB AI: birinchi ishlaydigan platforma (Flask + SQLite)."""
import os
import re
import sqlite3
from flask import Flask, render_template, request, g, abort

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "biolab.db")
app = Flask(__name__)

# NAMUNA ma'lumotlar. IUCN holatini iucnredlist.org dan tekshiring!
SEED = [
    ("Qor qoploni", "Panthera uncia", "Mammalia", "Carnivora", "Felidae",
     "Markaziy va Janubiy Osiyo tog'larida yashaydigan yirtqich mushuksimon.",
     "Vulnerable (zaif)", "Wikipedia", "https://en.wikipedia.org/wiki/Snow_leopard"),
    ("Afrika savanna fili", "Loxodonta africana", "Mammalia", "Proboscidea", "Elephantidae",
     "Quruqlikdagi eng katta hayvon. Ijtimoiy hayvon, podalarda yashaydi.",
     "Endangered (xavf ostida)", "Wikipedia", "https://en.wikipedia.org/wiki/African_bush_elephant"),
    ("Katta panda", "Ailuropoda melanoleuca", "Mammalia", "Carnivora", "Ursidae",
     "Xitoy tog' o'rmonlarida yashaydi, asosan bambuk bilan oziqlanadi.",
     "Vulnerable (zaif)", "Wikipedia", "https://en.wikipedia.org/wiki/Giant_panda"),
    ("Kulrang bo'ri", "Canis lupus", "Mammalia", "Carnivora", "Canidae",
     "Shimoliy yarimsharda keng tarqalgan, oilaviy to'dalarda yashaydigan yirtqich.",
     "Least Concern (xavotir kam)", "Wikipedia", "https://en.wikipedia.org/wiki/Wolf"),
    ("Ko'k kit", "Balaenoptera musculus", "Mammalia", "Artiodactyla", "Balaenopteridae",
     "Yer tarixidagi eng katta ma'lum hayvon. Asosan kril bilan oziqlanadi.",
     "Endangered (xavf ostida)", "Wikipedia", "https://en.wikipedia.org/wiki/Blue_whale"),
    ("Shoh lochin (peregrin lochini)", "Falco peregrinus", "Aves", "Falconiformes", "Falconidae",
     "Havoda juda tez uchadigan yirtqich qush, dunyoning ko'p joyida uchraydi.",
     "Least Concern (xavotir kam)", "Wikipedia", "https://en.wikipedia.org/wiki/Peregrine_falcon"),
    ("Nil timsohi", "Crocodylus niloticus", "Reptilia", "Crocodilia", "Crocodylidae",
     "Afrikaning chuchuk suv havzalarida yashaydigan yirik timsoh.",
     "Least Concern (xavotir kam)", "Wikipedia", "https://en.wikipedia.org/wiki/Nile_crocodile"),
    ("Oddiy delfin (afalina)", "Tursiops truncatus", "Mammalia", "Artiodactyla", "Delphinidae",
     "Aqlli va ijtimoiy dengiz sutemizuvchisi, ovoz signallari bilan muloqot qiladi.",
     "Least Concern (xavotir kam)", "Wikipedia", "https://en.wikipedia.org/wiki/Common_bottlenose_dolphin"),
    ("Saygak", "Saiga tatarica", "Mammalia", "Artiodactyla", "Bovidae",
     "Dasht antilopasi, Qozog'iston va atrofida yashaydi, o'ziga xos shishgan burni bor.",
     "Near Threatened (xavfga yaqin)", "Wikipedia", "https://en.wikipedia.org/wiki/Saiga_antelope"),
    ("Qo'ng'ir ayiq", "Ursus arctos", "Mammalia", "Carnivora", "Ursidae",
     "Shimoliy yarimsharda keng tarqalgan, hamma narsa yeydigan yirik ayiq.",
     "Least Concern (xavotir kam)", "Wikipedia", "https://en.wikipedia.org/wiki/Brown_bear"),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""CREATE TABLE IF NOT EXISTS species (
        id INTEGER PRIMARY KEY,
        name_uz TEXT NOT NULL,
        name_latin TEXT NOT NULL UNIQUE,
        class_name TEXT NOT NULL,
        order_name TEXT NOT NULL,
        family TEXT NOT NULL,
        description TEXT NOT NULL,
        iucn_status TEXT NOT NULL,
        source_name TEXT NOT NULL,
        source_url TEXT NOT NULL)""")
    if db.execute("SELECT COUNT(*) FROM species").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO species (name_uz,name_latin,class_name,order_name,family,"
            "description,iucn_status,source_name,source_url) VALUES (?,?,?,?,?,?,?,?,?)",
            SEED)
    db.commit()
    db.close()


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    db = get_db()
    if q:
        like = f"%{q}%"
        rows = db.execute(
            "SELECT * FROM species WHERE name_uz LIKE ? OR name_latin LIKE ? "
            "ORDER BY name_uz", (like, like)).fetchall()
    else:
        rows = db.execute("SELECT * FROM species ORDER BY name_uz").fetchall()
    return render_template("index.html", species=rows, q=q)


@app.route("/species/<int:sid>")
def species(sid):
    row = get_db().execute("SELECT * FROM species WHERE id=?", (sid,)).fetchone()
    if row is None:
        abort(404)
    return render_template("species.html", s=row)


@app.route("/compare")
def compare():
    db = get_db()
    all_sp = db.execute("SELECT id, name_uz FROM species ORDER BY name_uz").fetchall()
    a = request.args.get("a", type=int)
    b = request.args.get("b", type=int)
    sa = db.execute("SELECT * FROM species WHERE id=?", (a,)).fetchone() if a else None
    sb = db.execute("SELECT * FROM species WHERE id=?", (b,)).fetchone() if b else None
    return render_template("compare.html", all_sp=all_sp, a=sa, b=sb)


STOP = {"va", "bu", "bilan", "uchun", "nima", "qanday", "haqida", "ayt", "menga",
        "qaysi", "kim", "bor", "yoki", "the", "is", "of"}


@app.route("/ask")
def ask():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        words = [w for w in re.findall(r"\w+", q.lower()) if len(w) > 2 and w not in STOP]
        rows = get_db().execute("SELECT * FROM species").fetchall()
        scored = []
        for r in rows:
            text = " ".join(str(r[k]) for k in (
                "name_uz", "name_latin", "class_name", "order_name", "family",
                "description", "iucn_status")).lower()
            score = sum(1 for w in words if w in text)
            if score:
                scored.append((score, r))
        scored.sort(key=lambda x: -x[0])
        results = [r for _, r in scored[:3]]
    return render_template("ask.html", q=q, results=results)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
