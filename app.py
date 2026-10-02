from flask import Flask, request, jsonify, render_template_string
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB = Path(__file__).with_name("deyimler.db")

HTML = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Deyim Dünyası</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
    color: #172033;
}

.container {
    width: min(850px, 92%);
    margin: 40px auto;
}

header {
    text-align: center;
    margin-bottom: 30px;
}

header h1 {
    font-size: 42px;
    margin-bottom: 8px;
}

header p {
    color: #667085;
}

.creator {
    background: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,.08);
    margin-bottom: 35px;
}

label {
    display: block;
    margin-top: 18px;
    margin-bottom: 7px;
    font-weight: bold;
}

input,
textarea,
select {
    width: 100%;
    padding: 13px;
    border: 1px solid #d0d5dd;
    border-radius: 10px;
    font-size: 16px;
    font-family: inherit;
}

textarea {
    min-height: 120px;
    resize: vertical;
}

button {
    border: 0;
    border-radius: 10px;
    padding: 13px 18px;
    cursor: pointer;
    font-size: 15px;
    font-weight: bold;
}

#publish {
    width: 100%;
    margin-top: 22px;
    background: #4f46e5;
    color: white;
}

#publish:hover {
    background: #4338ca;
}

#publish:disabled {
    opacity: .6;
    cursor: wait;
}

.feed-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

#refresh {
    background: white;
    border: 1px solid #d0d5dd;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    margin-top: 15px;
    box-shadow: 0 6px 25px rgba(0,0,0,.06);
}

.language {
    display: inline-block;
    padding: 6px 11px;
    background: #eef2ff;
    border-radius: 999px;
    font-size: 13px;
    margin-bottom: 10px;
}

.card h3 {
    font-size: 25px;
    margin: 5px 0 15px;
}

.meaning {
    color: #475467;
    line-height: 1.6;
}

#message {
    min-height: 20px;
    margin-bottom: 0;
    color: #475467;
}
</style>
</head>

<body>

<div class="container">

<header>
    <h1>🌍 Deyim Dünyası</h1>
    <p>Kendi deyimini oluştur ve dünyanın geri kalanıyla paylaş.</p>
</header>

<section class="creator">

<h2>➕ Yeni Deyim Oluştur</h2>

<label>Deyim</label>
<input
    id="deyim"
    maxlength="200"
    placeholder="Örn. Bulutun cebini dikmek"
>

<label>Anlamı</label>
<textarea
    id="anlam"
    maxlength="1000"
    placeholder="Bu deyimin senin için anlamı nedir?"
></textarea>

<label>Dil</label>

<select id="dil">
    <option value="">Dil seç</option>
    <option value="🇹🇷 Türkçe">🇹🇷 Türkçe</option>
    <option value="🇬🇧 English">🇬🇧 English</option>
    <option value="🇩🇪 Deutsch">🇩🇪 Deutsch</option>
    <option value="🇫🇷 Français">🇫🇷 Français</option>
    <option value="🇪🇸 Español">🇪🇸 Español</option>
    <option value="🇮🇹 Italiano">🇮🇹 Italiano</option>
    <option value="🇯🇵 日本語">🇯🇵 日本語</option>
    <option value="🇰🇷 한국어">🇰🇷 한국어</option>
    <option value="🇵🇹 Português">🇵🇹 Português</option>
    <option value="🇷🇺 Русский">🇷🇺 Русский</option>
    <option value="🇨🇳 中文">🇨🇳 中文</option>
    <option value="🌐 Diğer">🌐 Diğer</option>
</select>

<button id="publish">
    🌍 Yayımla
</button>

<p id="message"></p>

</section>

<section>

<div class="feed-header">
    <h2>📚 Yayımlanan Deyimler</h2>
    <button id="refresh">↻ Yenile</button>
</div>

<div id="feed"></div>

</section>

</div>

<script>

const deyim = document.getElementById("deyim");
const anlam = document.getElementById("anlam");
const dil = document.getElementById("dil");
const publish = document.getElementById("publish");
const refresh = document.getElementById("refresh");
const feed = document.getElementById("feed");
const message = document.getElementById("message");

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function loadDeyimler() {

    try {

        const response = await fetch("/api/deyimler");
        const items = await response.json();

        feed.innerHTML = "";

        if (items.length === 0) {

            feed.innerHTML =
                "<p>Henüz hiç deyim yok. İlk deyimi sen oluştur!</p>";

            return;
        }

        items.forEach(item => {

            const card = document.createElement("article");

            card.className = "card";

            card.innerHTML = `
                <div class="language">
                    ${escapeHTML(item.dil)}
                </div>

                <h3>
                    ${escapeHTML(item.deyim)}
                </h3>

                <div class="meaning">
                    <strong>Anlamı:</strong>
                    ${escapeHTML(item.anlam)}
                </div>
            `;

            feed.appendChild(card);

        });

    } catch {

        feed.innerHTML =
            "<p>Deyimler yüklenemedi.</p>";

    }
}

publish.addEventListener("click", async () => {

    const deyimValue = deyim.value.trim();
    const anlamValue = anlam.value.trim();
    const dilValue = dil.value;

    if (!deyimValue || !anlamValue || !dilValue) {

        message.textContent =
            "Lütfen deyim, anlam ve dil alanlarını doldur.";

        return;
    }

    publish.disabled = true;

    message.textContent = "Yayımlanıyor...";

    try {

        const response = await fetch("/api/deyimler", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                deyim: deyimValue,
                anlam: anlamValue,
                dil: dilValue
            })

        });

        const result = await response.json();

        if (!response.ok) {

            message.textContent =
                result.error || "Yayımlama başarısız.";

            return;
        }

        deyim.value = "";
        anlam.value = "";
        dil.value = "";

        message.textContent =
            "✅ Deyimin herkese açık olarak yayımlandı!";

        await loadDeyimler();

    } catch {

        message.textContent =
            "Sunucuya ulaşılamadı.";

    } finally {

        publish.disabled = false;

    }

});

refresh.addEventListener("click", loadDeyimler);

loadDeyimler();

</script>

</body>
</html>
"""


def init_database():

    with sqlite3.connect(DB) as db:

        db.execute("""
            CREATE TABLE IF NOT EXISTS deyimler (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                deyim TEXT NOT NULL,

                anlam TEXT NOT NULL,

                dil TEXT NOT NULL,

                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        db.commit()


@app.route("/")
def home():

    return render_template_string(HTML)


@app.route("/api/deyimler", methods=["GET"])
def get_deyimler():

    with sqlite3.connect(DB) as db:

        db.row_factory = sqlite3.Row

        rows = db.execute("""
            SELECT id, deyim, anlam, dil, tarih
            FROM deyimler
            ORDER BY id DESC
        """).fetchall()

    return jsonify([dict(row) for row in rows])


@app.route("/api/deyimler", methods=["POST"])
def add_deyim():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Geçersiz veri."
        }), 400

    deyim = str(data.get("deyim", "")).strip()
    anlam = str(data.get("anlam", "")).strip()
    dil = str(data.get("dil", "")).strip()

    if not deyim or not anlam or not dil:

        return jsonify({
            "error": "Deyim, anlam ve dil zorunludur."
        }), 400

    if len(deyim) > 200:

        return jsonify({
            "error": "Deyim çok uzun."
        }), 400

    if len(anlam) > 1000:

        return jsonify({
            "error": "Anlam çok uzun."
        }), 400

    with sqlite3.connect(DB) as db:

        cursor = db.execute(
            """
            INSERT INTO deyimler
            (deyim, anlam, dil)
            VALUES (?, ?, ?)
            """,
            (deyim, anlam, dil)
        )

        db.commit()

        new_id = cursor.lastrowid

    return jsonify({
        "id": new_id,
        "deyim": deyim,
        "anlam": anlam,
        "dil": dil
    }), 201


init_database()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )