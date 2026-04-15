# -*- coding: utf-8 -*-
"""
Moment Tabiat Parkı — PDF Motor v1
Tüm bölümler data dict'e göre dinamik — boş bölümler PDF'e girmez
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, BaseDocTemplate, PageTemplate, Frame
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from datetime import datetime, timedelta
import os

# Font path — proje kök dizininde ara, sonra alt klasörler, sonra sistem
_DIR = os.path.dirname(os.path.abspath(__file__))
_FONT_DIRS = [
    _DIR,
    os.path.join(_DIR, "fonts"),
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/dejavu",
    "/usr/local/share/fonts",
]

def _find_font(name):
    for d in _FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError("Font bulunamadi: " + name + " | Aranan: " + str(_FONT_DIRS))

pdfmetrics.registerFont(TTFont("DV",   _find_font("DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DV-B", _find_font("DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DV-I", _find_font("DejaVuSans-Oblique.ttf")))

C_INK    = HexColor("#2A1F14")
C_BARK   = HexColor("#5C3D1E")
C_SAND   = HexColor("#C4A882")
C_GOLD   = HexColor("#A07840")
C_GOLD2  = HexColor("#C49A58")
C_PARCH  = HexColor("#F7F0E4")
C_PARCH2 = HexColor("#EDE3D0")
C_LINEN  = HexColor("#FAF7F2")
C_BORDER = HexColor("#D5C8B0")
C_MUTED  = HexColor("#8C7B68")
C_WHITE  = white
W = 170*mm

def S(n,**k):
    d=dict(fontName="DV",fontSize=10,leading=15,textColor=C_INK)
    d.update(k); return ParagraphStyle(n,**d)

def Ep(): return Paragraph("",S("ep"))

S_GREET = S("gr",  fontSize=10,    leading=16)
S_LABEL = S("la",  fontName="DV-B",fontSize=9,   textColor=C_BARK)
S_VALUE = S("va",  fontSize=9.5,   leading=14)
S_SEC   = S("sc",  fontName="DV-B",fontSize=9,   textColor=C_WHITE, alignment=TA_CENTER)
S_MT    = S("mt",  fontName="DV-B",fontSize=11,  textColor=C_INK,   alignment=TA_CENTER)
S_MI    = S("mi",  fontSize=9,     alignment=TA_CENTER, leading=13)
S_FOOT  = S("ft",  fontSize=7.5,   textColor=C_MUTED,  alignment=TA_CENTER)
S_SIG   = S("si",  fontName="DV-B",fontSize=10.5,textColor=C_INK)
S_BUL   = S("bu",  fontSize=9.5,   leading=14)
S_PH    = S("ph",  fontName="DV-B",fontSize=9,   textColor=C_INK)
S_PH2   = S("ph2", fontName="DV-B",fontSize=8,   textColor=C_INK)
S_VA2   = S("va2", fontSize=8.5,   leading=13)
S_DET   = S("dt",  fontSize=8.5,   textColor=C_MUTED, leading=13)

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_v2.png")

# ── HEADER ─────────────────────────────────────────────────────────
class Header(Flowable):
    def __init__(self, w=W):
        super().__init__()
        self.width  = w
        self.height = 90*mm

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        top_h = 38*mm

        c.setFillColor(C_PARCH2)
        c.rect(0, h-top_h, w, top_h, fill=1, stroke=0)

        # Logo sol
        try:
            img = ImageReader(LOGO_PATH)
            c.drawImage(img, 4*mm, h-top_h+(top_h-27*mm)/2,
                        width=36*mm, height=27*mm,
                        mask='auto', preserveAspectRatio=True, anchor='w')
        except: pass

        # moment. + alt bilgiler — tek sütun, tam ortada
        cx = w/2
        top_center = h - top_h/2 + 2*mm   # dikey merkez biraz yukarı

        # moment.
        c.setFillColor(C_INK)
        c.setFont("DV-B", 22)
        c.drawCentredString(cx, top_center + 8*mm, "moment.")

        # Alt bilgiler tek sütun halinde, moment yazısının tam altında
        info_y = top_center + 2*mm
        c.setFillColor(C_MUTED)
        c.setFont("DV", 7.5)
        c.drawCentredString(cx, info_y, "T A B İ A T   P A R K I")

        # İnce çizgi
        c.setStrokeColor(C_SAND)
        c.setLineWidth(0.4)
        c.line(cx - 18*mm, info_y - 2.5*mm, cx + 18*mm, info_y - 2.5*mm)

        # İletişim bilgileri alt alta tek sütun
        c.setFillColor(C_BARK)
        c.setFont("DV", 7.2)
        c.drawCentredString(cx, info_y - 7*mm, "+90 532 441 18 11")
        c.drawCentredString(cx, info_y - 11.5*mm, "info@moment.com.tr")
        c.drawCentredString(cx, info_y - 16*mm, "moment.com.tr")

        # Ayırıcı
        c.setFillColor(C_GOLD)
        c.rect(0, h-42*mm, w, 1.5*mm, fill=1, stroke=0)
        c.setFillColor(C_SAND)
        c.rect(0, h-42.7*mm, w, 0.4*mm, fill=1, stroke=0)

        # Slogan zemin
        c.setFillColor(C_LINEN)
        c.rect(0, 0, w, h-44*mm, fill=1, stroke=0)

        mid = (h-44*mm)/2
        c.setFillColor(C_GOLD)
        c.setFont("DV-I", 8.5)
        c.drawCentredString(w/2, mid+8*mm,
            u'"Küçük şeylerin büyük anlamlar ifade ettiği" Moment\'de,')
        c.setFillColor(C_INK)
        c.setFont("DV-B", 12.5)
        c.drawCentredString(w/2, mid,
            u"Doğanın kalbinde her organizasyon bir macera,")
        c.setFillColor(C_GOLD)
        c.setFont("DV-B", 12.5)
        c.drawCentredString(w/2, mid-8*mm, u"her an bir hatıra.")

        c.setStrokeColor(C_BORDER)
        c.setLineWidth(0.4)
        c.line(20*mm, 2*mm, w-20*mm, 2*mm)

    def wrap(self,*a): return self.width, self.height

# ── YARDIMCI FONKSİYONLAR ──────────────────────────────────────────
def sec(text):
    t=Table([[Paragraph(text,S_SEC)]],colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),C_INK),
        ("LINEBELOW",(0,0),(-1,-1),2,C_GOLD2),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),10),
    ]))
    return t

def info2(left,right):
    m=max(len(left),len(right))
    while len(left)<m: left.append(("",""))
    while len(right)<m: right.append(("",""))
    rows=[]
    for (lk,lv),(rk,rv) in zip(left,right):
        rows.append([Paragraph(lk,S_LABEL),Paragraph(lv or "—",S_VALUE),
                     Ep(),Paragraph(rk,S_LABEL),Paragraph(rv or "—",S_VALUE)])
    t=Table(rows,colWidths=[24*mm,52*mm,5*mm,28*mm,61*mm])
    t.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),
        ("LINEBELOW",(0,0),(-1,-1),0.3,C_BORDER),
    ]))
    return t

def org_tbl(d):
    cols=["TARİH","ETKİNLİK","ALAN","SAAT","KİŞİ","DÜZEN"]
    vals=[d.get("tarih","—"),d.get("etkinlik_turu","—"),d.get("alan","—"),
          d.get("saat","—"),d.get("kisi","—"),d.get("duzen","—")]
    t=Table([[Paragraph(c,S_PH2) for c in cols],
             [Paragraph(str(v),S_VA2) for v in vals]],
            colWidths=[28*mm,30*mm,32*mm,28*mm,20*mm,32*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),C_PARCH),
        ("LINEBELOW",(0,0),(-1,0),1.5,C_GOLD2),
        ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    return t

def price_tbl(items,kdv=0.20):
    hdr=[Paragraph(h,S_PH) for h in ["KALEM","BİRİM FİYAT","MİKTAR","TUTAR"]]
    rows=[hdr]; total=0
    for item in items:
        label,up,qty,unit=item[0],item[1],item[2],item[3]
        detail=item[4] if len(item)>4 else None
        sub=up*qty; total+=sub
        if detail:
            cell=Table([[Paragraph(label,S_VALUE)],[Paragraph(detail,S_DET)]],
                       colWidths=[86*mm])
            cell.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),0),
                ("BOTTOMPADDING",(0,0),(-1,-1),0),("LEFTPADDING",(0,0),(-1,-1),0),
                ("RIGHTPADDING",(0,0),(-1,-1),0)]))
        else:
            cell=Paragraph(label,S_VALUE)
        # Fiyatı temiz göster: 250.0 → 250, 250.5 → 250,5
        up_str = str(int(up)) if up == int(up) else f"{up:,.2f}".rstrip('0').rstrip(',')
        qty_str = str(int(qty)) if qty == int(qty) else str(qty)
        rows.append([cell,Paragraph(f"{up_str} TL",S_VALUE),
            Paragraph(f"{qty_str} {unit}",S_VALUE),Paragraph(f"{sub:,.0f} TL",S_VALUE)])
    kv=total*kdv; gd=total+kv
    rows+=[
        [Paragraph("Ara Toplam",S_LABEL),Ep(),Ep(),Paragraph(f"{total:,.0f} TL",S_VALUE)],
        [Paragraph(f"KDV (%{int(kdv*100)})",S_LABEL),Ep(),Ep(),Paragraph(f"{kv:,.0f} TL",S_VALUE)],
        [Paragraph("GENEL TOPLAM",S("gt",fontName="DV-B",fontSize=12,textColor=C_INK)),
         Ep(),Ep(),Paragraph(f"{gd:,.0f} TL",S("gp",fontName="DV-B",fontSize=12,
             textColor=C_GOLD,alignment=TA_RIGHT))],
    ]
    sp=len(items)+1
    t=Table(rows,colWidths=[88*mm,28*mm,24*mm,30*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),C_PARCH),("LINEBELOW",(0,0),(-1,0),1.5,C_GOLD2),
        ("GRID",(0,0),(-1,len(items)),0.3,C_BORDER),
        ("LINEABOVE",(0,sp),(-1,sp),0.5,C_SAND),
        ("SPAN",(0,sp),(2,sp)),("SPAN",(0,sp+1),(2,sp+1)),("SPAN",(0,sp+2),(2,sp+2)),
        ("BACKGROUND",(0,sp+2),(-1,sp+2),C_PARCH),
        ("LINEABOVE",(0,sp+2),(-1,sp+2),2,C_GOLD),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("ALIGN",(1,0),(-1,-1),"RIGHT"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    return t,gd

def menu_cols(kategoriler):
    n=len(kategoriler); cw=W/n
    cols=[[Paragraph(c["title"],S_MT)]+[Paragraph(it,S_MI) for it in c["items"]]
          for c in kategoriler]
    maxr=max(len(c) for c in cols)
    for c in cols:
        while len(c)<maxr: c.append(Paragraph("",S_MI))
    data=[[cols[ci][ri] for ci in range(n)] for ri in range(maxr)]
    t=Table(data,colWidths=[cw]*n)
    t.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LINEAFTER",(0,0),(-2,-1),0.5,C_BORDER),
        ("BOX",(0,0),(-1,-1),0.5,C_BORDER),
        ("BACKGROUND",(0,0),(-1,0),C_PARCH),
        ("LINEBELOW",(0,0),(-1,0),1.5,C_GOLD2),
    ]))
    return t

def parse_date(s):
    for f in ["%d/%m/%Y","%d.%m.%Y"]:
        try: return datetime.strptime(s.strip(),f)
        except: pass
    return None

def pay_tbl(gd,tip,org_tarih,pay_rows=None):
    dt=parse_date(org_tarih.split("–")[0].strip() if "–" in org_tarih else org_tarih)
    son=(dt-timedelta(days=1)).strftime("%d/%m/%Y") if dt else "Organizasyondan 1 gün önce"
    if tip=="50_50":
        rows=[["1. Ödeme — %50 Ön Ödeme  (Sözleşme imzasında)",f"{gd*.5:,.0f} TL"],
              [f"2. Ödeme — %50 Kalan  ·  Son ödeme: {son}",f"{gd*.5:,.0f} TL"]]
    elif tip=="40_30_30":
        rows=[["1. Ödeme — %40 Ön Ödeme  (Sözleşme imzasında)",f"{gd*.4:,.0f} TL"],
              ["2. Ödeme — %30 Ara Ödeme",f"{gd*.3:,.0f} TL"],
              [f"3. Ödeme — %30 Kalan  ·  Son ödeme: {son}",f"{gd*.3:,.0f} TL"]]
    elif tip=="manuel" and pay_rows:
        rows=[[r.get("l","Ödeme"),
               (f"{float(r['t']):,.0f} TL" if r.get("t") else "")+(f" ({r['o']})" if r.get("o") else "")]
              for r in pay_rows]
    else:
        rows=[[f"Tam Ödeme  ·  Son ödeme: {son}",f"{gd:,.0f} TL"]]
    hdr=[[Paragraph("ÖDEME PLANI",S_PH),Paragraph("TUTAR",S_PH)]]
    data=hdr+[[Paragraph(r[0],S_VALUE),Paragraph(r[1],S_VALUE)] for r in rows]
    t=Table(data,colWidths=[130*mm,40*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),C_PARCH),("LINEBELOW",(0,0),(-1,0),1.5,C_GOLD2),
        ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
        ("ALIGN",(1,0),(1,-1),"RIGHT"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
    ]))
    return t

def bank_tbl(ad,banka,sube,iban):
    hdr=[[Paragraph(h,S_PH) for h in ["HESAP ADI","BANKA","ŞUBE","IBAN"]]]
    row=[[Paragraph(v,S_VALUE) for v in [ad,banka,sube,iban]]]
    t=Table(hdr+row,colWidths=[58*mm,18*mm,18*mm,76*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),C_PARCH),("LINEBELOW",(0,0),(-1,0),1.5,C_GOLD2),
        ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
    ]))
    return t

def bul(txt): return Paragraph(f"<bullet>▪</bullet> {txt}",S_BUL)
def kt(*items): return KeepTogether(list(items))

# ══════════════════════════════════════════════════════════════════
# ANA BUILD FONKSİYONU — data dict ile tam dinamik
# ══════════════════════════════════════════════════════════════════
def build_pdf(data, out_path):
    """
    data dict anahtarları:
      musteri_adi, musteri_email, musteri_tel, musteri_unvan
      gonderen, gonderen_email, gonderen_tel, teklif_tar
      tarih, saat, kisi, etkinlik_turu, alan, duzen
      kdv_orani (float, ör: 0.20)
      odeme_tipi ('50_50','40_30_30','tam','manuel')
      pay_rows (liste, manuel ödeme için)
      opsiyon, rezervasyon
      h_ad, h_banka, h_sube, h_iban
      fiyat_kalemleri: [(label, unit_price, qty, unit, detail_or_None), ...]
      notlar: [str, ...]
      dahil_hizmetler: [str, ...]  ← boşsa bölüm çıkmaz
      menuler: [{baslik, kategoriler:[{title,items}]}]  ← boşsa çıkmaz
      park_aktiviteleri: [{name,icon,price,unit,not}]  ← boşsa çıkmaz
      etkinlikler: [{ad,fiyat,unit}]  ← boşsa çıkmaz
      flow: [str]  ← boşsa çıkmaz
      kapanis_metin: str
    """
    PW, PH = A4

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(HexColor("#2A1F14"))
        canvas.rect(0, 0, PW, 8, fill=1, stroke=0)
        canvas.setFillColor(HexColor("#A07840"))
        canvas.rect(0, 8, PW, 3, fill=1, stroke=0)
        canvas.setFillColor(HexColor("#C4A882"))
        canvas.rect(0, 11, PW, 1.2, fill=1, stroke=0)
        canvas.setFillColor(HexColor("#FAF7F2"))
        canvas.setFont("DV", 7)
        canvas.drawCentredString(PW/2, 2.5, str(doc.page))
        canvas.restoreState()

    frame=Frame(20*mm,18*mm,170*mm,262*mm,
                leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    doc=BaseDocTemplate(out_path,pagesize=A4,
        leftMargin=20*mm,rightMargin=20*mm,
        topMargin=15*mm,bottomMargin=18*mm)
    template=PageTemplate(id="main",frames=[frame],onPage=on_page)
    doc.addPageTemplates([template])

    s=[]
    kdv = float(data.get("kdv_orani", 0.20))
    musteri = data.get("musteri_adi","Değerli Müşterimiz")
    tarih   = data.get("tarih","")
    rez_map = {"on":"Ön rezervasyon yapılmıştır.",
               "on_rezervasyon":"Ön rezervasyon yapılmıştır.",
               "kesin":"Kesin rezervasyon yapılmıştır."}

    # ── HEADER ────────────────────────────────────────────────────
    s.append(Header())
    s.append(Spacer(1,12))

    # ── BİLGİLER ──────────────────────────────────────────────────
    gonderen_str = data.get("gonderen","Ebru Akyürekli")
    s.append(kt(
        info2(
            left=[
                ("İsim",    data.get("musteri_adi","")),
                ("E-mail",  data.get("musteri_email","")),
                ("Telefon", data.get("musteri_tel","")),
            ],
            right=[
                ("Gönderen", gonderen_str),
                ("E-mail",   data.get("gonderen_email","info@moment.com.tr")),
                ("Telefon",  data.get("gonderen_tel","+90 5304637090")),
                ("Tarih",    data.get("teklif_tar","")),
            ]
        ),
        Spacer(1,10),
    ))

    # ── SELAMLAMA ─────────────────────────────────────────────────
    s.append(Spacer(1,4))
    s.append(Paragraph(f"Sayın {musteri},",S_GREET))
    s.append(Spacer(1,5))
    s.append(Paragraph(
        "Moment Tabiat Parkı olarak bize göstermiş olduğunuz ilgi için teşekkür ederiz. "
        "Talepleriniz doğrultusunda size özel hazırladığımız teklif detaylarımız "
        "aşağıda dikkatinize sunulmuştur.",S_GREET))
    s.append(Spacer(1,14))

    # ── ORG DETAY ─────────────────────────────────────────────────
    s.append(kt(
        sec("ORGANİZASYON DETAYLARI"),
        Spacer(1,6),
        org_tbl(data),
        Spacer(1,12),
    ))

    # ── FİYAT ─────────────────────────────────────────────────────
    price_items = data.get("fiyat_kalemleri",[])
    # Park aktivitelerini fiyat tablosuna ekle
    for ak in data.get("park_aktiviteleri",[]):
        if ak.get("price"):
            unit = ak.get("unit","kişi")
            # toplam birimse miktar 1, kişi birimse kişi sayısı
            qty = 1 if unit == "toplam" else float(ak.get("qty",1) or 1)
            price_items = list(price_items) + [(
                ak["name"], float(ak["price"]), qty,
                unit, ak.get("not","")
            )]
    # Seçilen etkinlikleri fiyat tablosuna ekle
    for et in data.get("etkinlikler",[]):
        if et.get("fiyat"):
            price_items = list(price_items) + [(
                et["ad"], float(et["fiyat"]), 1, et.get("unit","toplam"), None
            )]

    if price_items:
        pt,gd = price_tbl(price_items, kdv)
        notlar_blok = [bul(n) for n in data.get("notlar",[]) if n]
        s.append(kt(
            sec("ORGANİZASYON PAKETİ"),Spacer(1,6),pt,Spacer(1,5),
            *notlar_blok,
            Spacer(1,12),
        ))
    else:
        gd = 0

    # ── DAHİL HİZMETLER — sadece varsa ───────────────────────────
    svcs = [v for v in data.get("dahil_hizmetler",[]) if v]
    if svcs:
        blk=[sec("ORGANİZASYONA DAHİL HİZMETLER"),Spacer(1,6)]
        for sv in svcs: blk.append(bul(sv))
        blk.append(Spacer(1,12))
        s.append(kt(*blk))

    # ── MENÜLER — sadece varsa ─────────────────────────────────────
    menuler = [m for m in data.get("menuler",[]) if m.get("baslik")]
    if menuler:
        s.append(kt(sec("MENÜLER"),Spacer(1,8)))
        for m in menuler:
            kats = [c for c in m.get("kategoriler",[]) if c.get("title") or c.get("items")]
            if kats:
                s.append(kt(
                    Paragraph(m["baslik"],S_MT),Spacer(1,6),
                    menu_cols(kats),Spacer(1,12),
                ))

    # ── AKTİVİTELER — sadece varsa ────────────────────────────────
    aktiviteler = data.get("park_aktiviteleri",[])
    if aktiviteler:
        act_rows=[[Paragraph(h,S_PH) for h in ["AKTİVİTE","FİYAT","BİRİM","DETAY"]]]
        for ak in aktiviteler:
            act_rows.append([
                Paragraph(f"{ak.get('icon','')} {ak['name']}".strip(),S_VALUE),
                Paragraph(f"{ak['price']:,.0f} TL" if ak.get("price") else "—",S_VALUE),
                Paragraph(ak.get("unit","kişi"),S_VALUE),
                Paragraph(ak.get("not",""),S_DET),
            ])
        at=Table(act_rows,colWidths=[52*mm,26*mm,22*mm,70*mm])
        at.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),C_PARCH),("LINEBELOW",(0,0),(-1,0),1.5,C_GOLD2),
            ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("ALIGN",(1,0),(2,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ]))
        s.append(kt(sec("MOMENT PARK AKTİVİTELERİ"),Spacer(1,6),at,Spacer(1,12)))

    # ── ETKİNLİKLER (opsiyonel liste) — sadece varsa ──────────────
    etkinlikler = data.get("etkinlikler",[])
    if etkinlikler:
        et_rows=[[Paragraph(h,S_PH) for h in ["ETKİNLİK","FİYAT","BİRİM"]]]
        for et in etkinlikler:
            et_rows.append([
                Paragraph(et["ad"],S_VALUE),
                Paragraph(f"{et['fiyat']:,.0f} TL + KDV" if et.get("fiyat") else "—",S_VALUE),
                Paragraph(et.get("unit","toplam"),S_VALUE),
            ])
        ett=Table(et_rows,colWidths=[100*mm,46*mm,24*mm])
        ett.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),C_PARCH),("LINEBELOW",(0,0),(-1,0),1.5,C_GOLD2),
            ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
            ("ALIGN",(1,0),(-1,-1),"RIGHT"),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ]))
        s.append(kt(sec("OPSİYONEL ETKİNLİKLER"),Spacer(1,6),ett,Spacer(1,12)))

    # ── AKIŞ NOTLARI — sadece varsa ───────────────────────────────
    flow = [f for f in data.get("flow",[]) if f]
    if flow:
        blk=[sec("ORGANİZASYON AKIŞI"),Spacer(1,6)]
        for f in flow: blk.append(bul(f))
        blk.append(Spacer(1,12))
        s.append(kt(*blk))

    # ── OPSİYON TARİHİ ────────────────────────────────────────────
    rez_txt = rez_map.get(data.get("rezervasyon",""),"")
    s.append(kt(
        sec("OPSİYON TARİHİ"),Spacer(1,6),
        Paragraph(f"Sayın {musteri},",S_GREET),Spacer(1,4),
        Paragraph(
            f"{rez_txt+' ' if rez_txt else ''}{data.get('alan','')} alanı, "
            f"<b>{tarih}</b> tarihi için tarafınıza ayrılmıştır."
            f"{' Teklifimiz <b>'+data['opsiyon']+'</b> tarihine kadar geçerlidir.' if data.get('opsiyon') else ''} "
            "Moment'e göstermiş olduğunuz ilgiye tekrar teşekkür eder, sizlere "
            "yardımcı olmaktan memnuniyet duyacağımızı belirtmek isteriz.",S_GREET),
        Spacer(1,12),
    ))

    # ── ÖDEME ─────────────────────────────────────────────────────
    if gd > 0:
        s.append(kt(
            sec("ÖDEME"),Spacer(1,6),
            pay_tbl(gd, data.get("odeme_tipi","50_50"), tarih,
                    data.get("pay_rows",[])),
            Spacer(1,7),
            bul("Sözleşmede imzalanan garanti kişi sayısının arttırımı ve azalması "
                "durumunda en geç 5 gün öncesinde yazılı haber verilmesi koşuluyla değişme kabul edilir."),
            bul("Bu rakam garanti kişi sayısının altında olduğu taktirde garanti kişi sayısından hesaplanacaktır."),
            Spacer(1,12),
        ))

    # ── BANKA ─────────────────────────────────────────────────────
    s.append(kt(
        Paragraph("MOMENT HESAP BİLGİLERİ",
            S("bh",fontName="DV-B",fontSize=9.5,textColor=C_INK,alignment=TA_CENTER)),
        Spacer(1,6),
        bank_tbl(
            data.get("h_ad","Moment Eğlence Sporları Merkezi Turizm San.Ve Dış.Tic.Aş."),
            data.get("h_banka","Enpara Bank A.Ş."),
            data.get("h_sube",""),
            data.get("h_iban","TR27 0015 7000 0000 0202 9803 77"),
        ),
        Spacer(1,12),
    ))

    # ── İMZA ──────────────────────────────────────────────────────
    s.append(Paragraph("Saygılarımızla,",S_GREET))
    s.append(Spacer(1,6))
    s.append(Paragraph(gonderen_str,S_SIG))

    # ── KAPANIŞ METNİ — sadece varsa ──────────────────────────────
    kapanis_metin = data.get("kapanis_metin") or "Moment’e göstermiş olduğunuz ilgiye tekrar teşekkür eder, sizlere yardımcı olmaktan memnuniyet duyacağımızı belirtmek isteriz."
    if kapanis_metin:
        s.append(Spacer(1,8))
        s.append(Paragraph(kapanis_metin,
            S("km",fontSize=9,textColor=C_BARK,fontName="DV-I",leading=14)))

    s.append(Spacer(1,10))
    s.append(Paragraph(
        "MOMENT TABİAT PARKI  ·  Çamlık Cad. No:1 Çiçekliköy Bornova İZMİR  ·  "
        "+90 532 441 18 11  ·  info@moment.com.tr  ·  moment.com.tr",S_FOOT))

    doc.build(s)
    return out_path

# Test
if __name__ == "__main__":
    test_data = {
        "musteri_adi":"Tuna Bey","musteri_email":"tuna@abc.com","musteri_tel":"0532 356 31 81",
        "gonderen":"Ebru Akyürekli","gonderen_email":"info@moment.com.tr",
        "gonderen_tel":"+90 5304637090","teklif_tar":"04/12/2025",
        "tarih":"14/12/2025","saat":"10:00-20:00","kisi":"150-200",
        "etkinlik_turu":"Şirket Piknik Organizasyonu",
        "alan":"Moment Bahçe (Alt+Üst)","duzen":"Uzun Masa Düzeni",
        "kdv_orani":0.20,"odeme_tipi":"50_50","rezervasyon":"on_rezervasyon",
        "fiyat_kalemleri":[
            ("Alan Kirası — Moment Bahçe",250,175,"kişi",None),
            ("Serpme Köy Kahvaltısı",390,175,"kişi",None),
            ("BBQ / Mangal Menüsü",680,175,"kişi",None),
            ("Kahve Servisi",50,175,"kişi",None),
        ],
        "notlar":["Fiyatımız organizasyonunuz için özeldir.",
                  "Tüm yiyecek içecek fiyatları + KDV'dir."],
        # Dahil hizmetler var
        "dahil_hizmetler":[
            "Moment Bahçe alanı organizasyon için kapatılacaktır.",
            "7 kişilik profesyonel catering ekibi görev alacaktır.",
            "Alana giriş ve otopark ücretsizdir.",
        ],
        # Menüler var
        "menuler":[
            {"baslik":"KAHVALTI MENÜ","kategoriler":[
                {"title":"Şarküteri","items":["Beyaz Peynir","Kaşar","Tulum","Siyah Zeytin","Yeşil Zeytin"]},
                {"title":"Sıcak Lezzetler","items":["Sigara Böreği","Patates Kızartması","Pişi","Haşlanmış Yumurta"]},
                {"title":"Fırından & İçecek","items":["Poğaça","Simit","Sınırsız Çay"]},
            ]},
            {"baslik":"BBQ MENÜ","kategoriler":[
                {"title":"Mangaldan","items":["Kasap Köfte (2 adet)","Tavuk İncik","Şiş Sucuk","Kuzu Şiş","Közlenmiş Biber","Elma Dilim Patates","Pirinç Pilavı"]},
                {"title":"Soğuk Büfe","items":["Patates Salatası","Yoğurtlu Patlıcan","Fava","Kuru Cacık"]},
                {"title":"Tatlı & İçecek","items":["Karagöz Tatlısı","Algida Dondurma","Sınırsız Su & Çay"]},
            ]},
        ],
        # Aktiviteler VAR
        "park_aktiviteleri":[
            {"name":"Parkur — Orman Macera","icon":"🌲","price":150,"qty":175,"unit":"kişi","not":"45 dk · Rehber eşliğinde"},
        ],
        # Opsiyonel etkinlikler YOK → bölüm çıkmayacak
        "etkinlikler":[],
        # Akış notları YOK
        "flow":[],
        "h_ad":"Moment Eğlence Sporları Merkezi Turizm San.Ve Dış.Tic.Aş.",
        "h_banka":"Enpara Bank A.Ş.","h_sube":"","h_iban":"TR27 0015 7000 0000 0202 9803 77",
    }
    result = build_pdf(test_data, "/home/claude/Moment_Test_Engine.pdf")
    import os
    print(f"✓ {result} ({os.path.getsize(result):,} bytes)")
