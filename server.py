# -*- coding: utf-8 -*-
"""
Moment Tabiat Parkı — Teklif Sistemi v3
SQLite veritabanı + takım girişi + teklif takibi
"""
from flask import Flask, request, send_file, jsonify, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, json, os, tempfile, functools
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'moment-tabiat-parki-2025-kalici-anahtar-x9k2m')
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30  # 30 gün
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

DB_PATH = os.environ.get('DB_PATH', '/tmp/moment.db')

# ── KULLANICILAR (env'den veya varsayılan) ─────────────────────────
def get_users():
    users_json = os.environ.get('MOMENT_USERS', '')
    if users_json:
        try:
            return json.loads(users_json)
        except:
            pass
    # Varsayılan kullanıcılar — production'da env variable ile override edin
    return [
        {"username": "ebru",   "password": generate_password_hash("moment2025"), "name": "Ebru Akyürekli", "role": "admin"},
        {"username": "takim",  "password": generate_password_hash("moment123"),  "name": "Takım Üyesi",    "role": "user"},
    ]

USERS = get_users()

# ── VERİTABANI ────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS musteriler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT NOT NULL,
        unvan TEXT,
        tel TEXT,
        email TEXT,
        not_ TEXT,
        olusturan TEXT,
        tarih TEXT,
        guncelleme TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS fiyatlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT NOT NULL,
        fiyat REAL,
        birim TEXT,
        kategori TEXT,
        olusturan TEXT,
        tarih TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS teklifler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        musteri_adi TEXT,
        musteri_email TEXT,
        musteri_tel TEXT,
        etkinlik_turu TEXT,
        alan TEXT,
        tarih TEXT,
        kisi TEXT,
        tutar REAL,
        kdv_orani REAL,
        durum TEXT DEFAULT 'bekliyor',
        hatirlatici_not TEXT,
        hatirlatici_tarih TEXT,
        gonderen TEXT,
        olusturan TEXT,
        olusturma_tarihi TEXT,
        guncelleme TEXT,
        teklif_data TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS sablonlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT NOT NULL,
        aciklama TEXT,
        data TEXT,
        olusturan TEXT,
        tarih TEXT
    )''')

    conn.commit()
    conn.close()

# ── AUTH ──────────────────────────────────────────────────────────
def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        user = next((u for u in USERS if u['username'] == session['username']), None)
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Yetkisiz erişim'}), 403
        return f(*args, **kwargs)
    return decorated

# ── SAYFALAR ──────────────────────────────────────────────────────
LOGIN_HTML = '''<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Moment — Giriş</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;
  background:#EDE3D0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#fff;border-radius:16px;padding:40px;width:100%;max-width:400px;
  box-shadow:0 8px 32px rgba(0,0,0,.12)}
.logo{text-align:center;margin-bottom:28px}
.logo-mark{font-size:36px;font-weight:700;color:#A07840;letter-spacing:2px}
.logo-sub{font-size:11px;color:#8C7B68;letter-spacing:3px;margin-top:4px}
.logo-line{width:60px;height:2px;background:#A07840;margin:10px auto 0}
h2{font-size:18px;font-weight:500;color:#2A1F14;margin-bottom:6px;text-align:center}
p{font-size:12px;color:#8C7B68;text-align:center;margin-bottom:24px}
.fld{margin-bottom:14px}
.fld label{display:block;font-size:11px;font-weight:500;color:#666;text-transform:uppercase;letter-spacing:.6px;margin-bottom:5px}
.fld input{width:100%;border:1.5px solid #e0e0e0;border-radius:8px;padding:10px 12px;font-size:13px;outline:none;transition:.2s;font-family:inherit}
.fld input:focus{border-color:#A07840}
.btn{width:100%;padding:12px;background:#A07840;color:#fff;border:none;border-radius:8px;
  font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;margin-top:6px;transition:.2s}
.btn:hover{background:#8a6820}
.err{background:#fde8e8;color:#b04030;padding:8px 12px;border-radius:7px;font-size:12px;margin-bottom:14px;text-align:center}
</style></head><body>
<div class="card">
  <div class="logo">
    <div class="logo-mark">moment.</div>
    <div class="logo-sub">T A B İ A T &nbsp; P A R K I</div>
    <div class="logo-line"></div>
  </div>
  <h2>Teklif Sistemi</h2>
  <p>Devam etmek için giriş yapın</p>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <form method="POST" action="/login">
    <div class="fld"><label>Kullanıcı Adı</label><input name="username" autofocus autocomplete="username"></div>
    <div class="fld"><label>Şifre</label><input name="password" type="password" autocomplete="current-password"></div>
    <button class="btn" type="submit">Giriş Yap →</button>
  </form>
</div>
</body></html>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Form veya fetch her ikisini destekle
        if request.is_json:
            data = request.get_json(force=True)
            username = data.get('username', '').strip()
            password = data.get('password', '')
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
        user = next((u for u in USERS if u['username'] == username), None)
        if user and check_password_hash(user['password'], password):
            session.permanent = True
            session['username'] = username
            session['name']     = user['name']
            session['role']     = user.get('role', 'user')
            if request.is_json:
                return jsonify({'ok': True, 'name': user['name']})
            return redirect('/')
        error = 'Kullanıcı adı veya şifre hatalı'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
@login_required
def index():
    with open(os.path.join(os.path.dirname(__file__), 'index.html'), encoding='utf-8') as f:
        html = f.read()
    # Kullanıcı bilgisini inject et
    user_info = json.dumps({'name': session.get('name'), 'username': session.get('username'), 'role': session.get('role')})
    html = html.replace('</head>', f'<script>window.CURRENT_USER={user_info};</script></head>', 1)
    return html

# ── PDF ────────────────────────────────────────────────────────────
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    if 'username' not in session:
        return jsonify({'error': 'Oturum süresi doldu, lütfen tekrar giriş yapın', 'code': 401}), 401
    try:
        data = request.get_json(force=True)
        fk = data.get('fiyat_kalemleri', [])
        data['fiyat_kalemleri'] = [tuple(x) for x in fk]
        data['kdv_orani'] = float(data.get('kdv_orani', 0.20))

        from moment_pdf_engine import build_pdf
        tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        tmp.close()
        build_pdf(data, tmp.name)

        # Teklifi veritabanına kaydet
        tutar = sum(float(x[1]) * float(x[2]) for x in fk if len(x) >= 3)
        tutar_kdv = tutar * (1 + data['kdv_orani'])
        save_teklif(data, tutar_kdv)

        musteri = data.get('musteri_adi', 'teklif').replace(' ', '_')
        tarih   = data.get('tarih', '').replace('/', '-').replace(' – ', '_')
        fname   = f"{musteri}_{tarih}_Teklif.pdf"

        return send_file(tmp.name, as_attachment=True, download_name=fname, mimetype='application/pdf')
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print('PDF ERROR:', str(e))
        print(tb)
        return jsonify({'error': str(e), 'trace': tb}), 500

def save_teklif(data, tutar):
    try:
        conn = get_db()
        conn.execute('''INSERT INTO teklifler
            (musteri_adi,musteri_email,musteri_tel,etkinlik_turu,alan,tarih,kisi,
             tutar,kdv_orani,durum,gonderen,olusturan,olusturma_tarihi,teklif_data)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            data.get('musteri_adi',''),
            data.get('musteri_email',''),
            data.get('musteri_tel',''),
            data.get('etkinlik_turu',''),
            data.get('alan',''),
            data.get('tarih',''),
            data.get('kisi',''),
            round(tutar, 2),
            data.get('kdv_orani', 0.20),
            'gonderildi',
            data.get('gonderen',''),
            session.get('username',''),
            datetime.now().strftime('%d/%m/%Y %H:%M'),
            json.dumps(data, ensure_ascii=False)
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print('Teklif kayıt hatası:', e)

# ── MÜŞTERİLER ────────────────────────────────────────────────────
@app.route('/api/musteriler', methods=['GET'])
@login_required
def get_musteriler():
    conn = get_db()
    rows = conn.execute('SELECT * FROM musteriler ORDER BY guncelleme DESC, tarih DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/musteriler', methods=['POST'])
@login_required
def save_musteri():
    d = request.get_json(force=True)
    now = datetime.now().strftime('%d/%m/%Y %H:%M')
    conn = get_db()
    existing = conn.execute('SELECT id FROM musteriler WHERE ad=?', (d.get('ad',''),)).fetchone()
    if existing:
        conn.execute('UPDATE musteriler SET unvan=?,tel=?,email=?,not_=?,guncelleme=? WHERE ad=?',
                     (d.get('unvan',''), d.get('tel',''), d.get('email',''), d.get('not_',''), now, d.get('ad','')))
    else:
        conn.execute('INSERT INTO musteriler (ad,unvan,tel,email,not_,olusturan,tarih,guncelleme) VALUES (?,?,?,?,?,?,?,?)',
                     (d.get('ad',''), d.get('unvan',''), d.get('tel',''), d.get('email',''), d.get('not_',''),
                      session.get('username',''), now, now))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/musteriler/<int:mid>', methods=['DELETE'])
@login_required
def delete_musteri(mid):
    conn = get_db()
    conn.execute('DELETE FROM musteriler WHERE id=?', (mid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── FİYATLAR ──────────────────────────────────────────────────────
@app.route('/api/fiyatlar', methods=['GET'])
@login_required
def get_fiyatlar():
    conn = get_db()
    rows = conn.execute('SELECT * FROM fiyatlar ORDER BY kategori, ad').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/fiyatlar', methods=['POST'])
@login_required
def save_fiyat():
    d = request.get_json(force=True)
    now = datetime.now().strftime('%d/%m/%Y %H:%M')
    conn = get_db()
    conn.execute('INSERT INTO fiyatlar (ad,fiyat,birim,kategori,olusturan,tarih) VALUES (?,?,?,?,?,?)',
                 (d.get('ad',''), float(d.get('fiyat',0)), d.get('birim','kişi'),
                  d.get('kategori','Genel'), session.get('username',''), now))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/fiyatlar/<int:fid>', methods=['PUT'])
@login_required
def update_fiyat(fid):
    d = request.get_json(force=True)
    conn = get_db()
    conn.execute('UPDATE fiyatlar SET ad=?,fiyat=?,birim=?,kategori=? WHERE id=?',
                 (d.get('ad',''), float(d.get('fiyat',0)), d.get('birim','kişi'), d.get('kategori','Genel'), fid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/fiyatlar/<int:fid>', methods=['DELETE'])
@login_required
def delete_fiyat(fid):
    conn = get_db()
    conn.execute('DELETE FROM fiyatlar WHERE id=?', (fid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── ŞABLONLAR ─────────────────────────────────────────────────────
@app.route('/api/sablonlar', methods=['GET'])
@login_required
def get_sablonlar():
    conn = get_db()
    rows = conn.execute('SELECT * FROM sablonlar ORDER BY tarih DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/sablonlar', methods=['POST'])
@login_required
def save_sablon():
    d = request.get_json(force=True)
    now = datetime.now().strftime('%d/%m/%Y %H:%M')
    conn = get_db()
    conn.execute('INSERT INTO sablonlar (ad,aciklama,data,olusturan,tarih) VALUES (?,?,?,?,?)',
                 (d.get('ad',''), d.get('aciklama',''),
                  json.dumps(d.get('data',{}), ensure_ascii=False),
                  session.get('username',''), now))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/sablonlar/<int:sid>', methods=['DELETE'])
@login_required
def delete_sablon(sid):
    conn = get_db()
    conn.execute('DELETE FROM sablonlar WHERE id=?', (sid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── TEKLİFLER ─────────────────────────────────────────────────────
@app.route('/api/teklifler', methods=['GET'])
@login_required
def get_teklifler():
    conn = get_db()
    rows = conn.execute('SELECT * FROM teklifler ORDER BY olusturma_tarihi DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/teklifler/<int:tid>/durum', methods=['PUT'])
@login_required
def update_durum(tid):
    d = request.get_json(force=True)
    now = datetime.now().strftime('%d/%m/%Y %H:%M')
    conn = get_db()
    conn.execute('UPDATE teklifler SET durum=?,guncelleme=? WHERE id=?',
                 (d.get('durum','bekliyor'), now, tid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/teklifler/<int:tid>/not', methods=['PUT'])
@login_required
def update_not(tid):
    d = request.get_json(force=True)
    now = datetime.now().strftime('%d/%m/%Y %H:%M')
    conn = get_db()
    conn.execute('UPDATE teklifler SET hatirlatici_not=?,hatirlatici_tarih=?,guncelleme=? WHERE id=?',
                 (d.get('not',''), d.get('tarih',''), now, tid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/teklifler/<int:tid>', methods=['DELETE'])
@login_required
def delete_teklif(tid):
    conn = get_db()
    conn.execute('DELETE FROM teklifler WHERE id=?', (tid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── İSTATİSTİK ────────────────────────────────────────────────────
@app.route('/api/istatistik', methods=['GET'])
@login_required
def get_istatistik():
    conn = get_db()
    rows = conn.execute('SELECT durum, tutar, olusturma_tarihi FROM teklifler').fetchall()
    conn.close()

    toplam = len(rows)
    kabul  = sum(1 for r in rows if r['durum'] == 'kabul')
    red    = sum(1 for r in rows if r['durum'] == 'reddedildi')
    bekl   = sum(1 for r in rows if r['durum'] in ('bekliyor','gonderildi'))
    ciro   = sum(r['tutar'] for r in rows if r['durum'] == 'kabul')
    bek_ciro = sum(r['tutar'] for r in rows if r['durum'] in ('bekliyor','gonderildi'))
    oran   = round(kabul / toplam * 100) if toplam > 0 else 0

    # Bu ay
    ay = datetime.now().strftime('%m/%Y')
    bu_ay = sum(1 for r in rows if r['olusturma_tarihi'] and ay in r['olusturma_tarihi'])

    return jsonify({
        'toplam': toplam, 'kabul': kabul, 'red': red, 'bekliyor': bekl,
        'kabul_orani': oran, 'ciro': round(ciro), 'beklenen_ciro': round(bek_ciro),
        'bu_ay': bu_ay
    })

# ── KULLANICI ─────────────────────────────────────────────────────
@app.route('/api/kullanici', methods=['GET'])
@login_required
def get_kullanici():
    return jsonify({'name': session.get('name'), 'username': session.get('username'), 'role': session.get('role')})

@app.route('/api/sifre', methods=['POST'])
@login_required
def change_sifre():
    d = request.get_json(force=True)
    username = session.get('username')
    user = next((u for u in USERS if u['username'] == username), None)
    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
    if not check_password_hash(user['password'], d.get('eski','')):
        return jsonify({'error': 'Mevcut şifre hatalı'}), 400
    user['password'] = generate_password_hash(d.get('yeni',''))
    return jsonify({'ok': True})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print(f'\n  ✓ Moment Teklif Sistemi → http://localhost:{port}\n')
    app.run(host='0.0.0.0', port=port, debug=False)

# Gunicorn için init
init_db()
