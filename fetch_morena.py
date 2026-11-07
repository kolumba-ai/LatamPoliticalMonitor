#!/usr/bin/env python3
"""Fetch the past month of TikTok videos by or about Morena politicians from the
Oriane API and write morena_data.json for the monitoring page.

Usage:  ORIANE_API_KEY=... python3 fetch_morena.py [days]
"""
import json, os, sys, time, urllib.request, urllib.error
from datetime import date, timedelta, datetime, timezone

API = "https://connect.oriane.xyz/rest/contents/search"
KEY = os.environ.get("ORIANE_API_KEY") or sys.exit("Set ORIANE_API_KEY")
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 30

# Each politician: names/phrases searched in caption, transcript and on-screen text,
# hashtags, and the Oriane profile id of their own TikTok account when indexed.
POLITICIANS = [
    # --- Dirigentes de Partido ---
    dict(slug="ariadna-montiel", name="Ariadna Montiel", role="Presidenta nacional de Morena; exsecretaria de Bienestar",
         cats=["dirigentes", "presidenciables"], names=["Ariadna Montiel"], tags=["ariadnamontiel"]),
    dict(slug="luisa-maria-alcalde", name="Luisa María Alcalde", role="Expresidenta nacional de Morena",
         cats=["presidenciables"], names=["Luisa María Alcalde", "Luisa Maria Alcalde"], tags=["luisamariaalcalde"]),
    dict(slug="carolina-rangel", name="Carolina Rangel", role="Secretaria general de Morena",
         cats=["dirigentes"], names=["Carolina Rangel"], tags=["carolinarangel"]),
    dict(slug="andres-lopez-beltran", name="Andrés López Beltrán", role="Secretario de organización de Morena",
         cats=["dirigentes", "presidenciables"], names=["Andrés López Beltrán", "Andres Lopez Beltran", "Andy López Beltrán", "Andy López"], tags=["andylopezbeltran", "andylopez"]),
    dict(slug="alfonso-durazo", name="Alfonso Durazo", role="Presidente del Consejo Nacional de Morena; gobernador de Sonora",
         cats=["dirigentes"], names=["Alfonso Durazo"], tags=["alfonsodurazo"]),
    dict(slug="citlalli-hernandez", name="Citlalli Hernández", role="Exsecretaria general de Morena; secretaria de las Mujeres",
         cats=["dirigentes"], names=["Citlalli Hernández", "Citlalli Hernandez"], tags=["citlallihernandez"],
         profile="prf_046c1eb859039cf109d0f2f1a23d"),
    # --- Presidentes Municipales ---
    dict(slug="aleida-alavez", name="Aleida Alavez", role="Alcaldesa de Iztapalapa, CDMX",
         cats=["municipales"], names=["Aleida Alavez"], tags=["aleidaalavez"]),
    dict(slug="janecarlo-lozano", name="Janecarlo Lozano", role="Alcalde de Gustavo A. Madero, CDMX",
         cats=["municipales"], names=["Janecarlo Lozano", "Janecarlo"], tags=["janecarlolozano"]),
    dict(slug="azucena-cisneros", name="Azucena Cisneros", role="Presidenta municipal de Ecatepec, Edomex",
         cats=["municipales"], names=["Azucena Cisneros"], tags=["azucenacisneros"]),
    dict(slug="abelina-lopez", name="Abelina López Rodríguez", role="Presidenta municipal de Acapulco, Gro.",
         cats=["municipales"], names=["Abelina López", "Abelina Lopez"], tags=["abelinalopez"],
         profile="prf_0aeaf9d60bb3d6af20080ce7f8a1"),
    dict(slug="ismael-burgueno", name="Ismael Burgueño", role="Presidente municipal de Tijuana, B.C.",
         cats=["municipales"], names=["Ismael Burgueño", "Ismael Burgueno"], tags=["ismaelburgueno"]),
    dict(slug="pepe-chedraui", name="Pepe Chedraui", role="Presidente municipal de Puebla, Pue.",
         cats=["municipales"], names=["Pepe Chedraui", "José Chedraui"], tags=["pepechedraui"]),
    dict(slug="cruz-perez-cuellar", name="Cruz Pérez Cuéllar", role="Presidente municipal de Ciudad Juárez; coordinador estatal de la 4T en Chihuahua",
         cats=["municipales"], names=["Cruz Pérez Cuéllar", "Cruz Perez Cuellar"], tags=["cruzperezcuellar"]),
    dict(slug="ana-miriam-ramos", name="Ana Miriam Ramos", role="Presidenta municipal de Culiacán, Sin.",
         cats=["municipales"], names=["Ana Miriam Ramos"], tags=["anamiriamramos"]),
    dict(slug="ana-paty-peralta", name="Ana Paty Peralta", role="Presidenta municipal de Benito Juárez (Cancún), Q. Roo",
         cats=["municipales"], names=["Ana Paty Peralta"], tags=["anapatyperalta"]),
    dict(slug="yolanda-osuna", name="Yolanda Osuna", role="Presidenta municipal de Centro (Villahermosa), Tab.",
         cats=["municipales"], names=["Yolanda Osuna"], tags=["yolandaosuna"]),
    dict(slug="javier-lopez-casarin", name="Javier López Casarín", role="Alcalde de Álvaro Obregón, CDMX (PVEM, coalición con Morena)",
         cats=["municipales"], names=["López Casarín", "Lopez Casarin"], tags=["javierlopezcasarin"],
         profile="prf_49b869fad575f76e7fb93a085756"),
    # --- Candidatos Presidenciables (2030) ---
    dict(slug="omar-garcia-harfuch", name="Omar García Harfuch", role="Secretario de Seguridad y Protección Ciudadana",
         cats=["presidenciables"], names=["García Harfuch", "Garcia Harfuch"], tags=["harfuch", "omargarciaharfuch"],
         profile="prf_cdd194cb8cabc359c6cfb773f8bf"),
    dict(slug="clara-brugada", name="Clara Brugada", role="Jefa de Gobierno de la Ciudad de México",
         cats=["presidenciables"], names=["Clara Brugada"], tags=["clarabrugada"],
         profile="prf_98cd31dc723a0b540054a5e97019"),
    dict(slug="marcelo-ebrard", name="Marcelo Ebrard", role="Secretario de Economía",
         cats=["presidenciables"], names=["Marcelo Ebrard"], tags=["marceloebrard"]),
    dict(slug="adan-augusto-lopez", name="Adán Augusto López", role="Senador",
         cats=["presidenciables"], names=["Adán Augusto", "Adan Augusto"], tags=["adanaugusto"]),
    dict(slug="ricardo-monreal", name="Ricardo Monreal", role="Coordinador de Morena y presidente de la Jucopo en la Cámara de Diputados",
         cats=["presidenciables"], names=["Ricardo Monreal"], tags=["ricardomonreal"]),
    dict(slug="rocio-nahle", name="Rocío Nahle", role="Gobernadora de Veracruz",
         cats=["presidenciables"], names=["Rocío Nahle", "Rocio Nahle"], tags=["rocionahle"],
         profile="prf_3605dae8f9d80885d583694cec4c"),
    dict(slug="gerardo-fernandez-norona", name="Gerardo Fernández Noroña", role="Senador",
         cats=["presidenciables"], names=["Fernández Noroña", "Fernandez Noroña", "Gerardo Noroña"], tags=["fernandeznorona", "gerardonorona"]),
    dict(slug="mario-delgado", name="Mario Delgado", role="Secretario de Educación Pública; expresidente de Morena",
         cats=["presidenciables"], names=["Mario Delgado"], tags=["mariodelgado"],
         profile="prf_3ec6038577c059aa6586914e1632"),
    dict(slug="ernestina-godoy", name="Ernestina Godoy", role="Fiscal General de la República",
         cats=["presidenciables"], names=["Ernestina Godoy"], tags=["ernestinagodoy"]),
    dict(slug="rosa-icela-rodriguez", name="Rosa Icela Rodríguez", role="Secretaria de Gobernación",
         cats=["presidenciables"], names=["Rosa Icela Rodríguez", "Rosa Icela Rodriguez"], tags=["rosaicelarodriguez"]),
]


def post(path_q, body):
    req = urllib.request.Request(API + path_q, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            payload = json.load(e)
            if e.code in (429, 502, 503, 504) and attempt < 3:
                time.sleep(2 * (attempt + 1)); continue
            return payload
        except (urllib.error.URLError, TimeoutError):
            if attempt < 3:
                time.sleep(2 * (attempt + 1)); continue
            raise


def query_for(p, after, before):
    text = {"includesExactly": {"values": p["names"], "operator": "or"}}
    anyof = {"caption": text, "transcript": text, "onScreenText": text,
             "hashtags": {"includesExactly": {"values": p["tags"], "operator": "or"}}}
    if p.get("profile"):
        anyof["profileId"] = {"includes": [p["profile"]]}
    return {"operator": "and",
            "filters": {"platform": {"includes": ["tiktok"]}, "format": {"includes": ["video"]},
                        "publishedAt": {"after": after, "before": before}},
            "queries": [{"operator": "or", "filters": anyof}]}


def main():
    today = date.today()
    after, before = (today - timedelta(days=DAYS)).isoformat(), today.isoformat()
    out = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "range": {"after": after, "before": before}, "politicians": []}
    for p in POLITICIANS:
        body, vids, offset, total = query_for(p, after, before), [], 0, None
        while True:
            d = post(f"?limit=100&offset={offset}&sort=viewsCount:desc", body)
            if "error" in d:
                if d["error"].get("code") != "OUT_OF_RANGE":
                    print(f"  ! {p['name']}: {d['error'].get('message')} {d['error'].get('context')}", file=sys.stderr)
                break
            total = d["metadata"]["pagination"]["totalCount"]
            for x in d["data"]["results"]:
                vids.append({
                    "id": x["platformId"], "handle": x["profileHandle"], "author": x["profileDisplayName"],
                    "caption": (x.get("caption") or x.get("title") or "").strip(),
                    "publishedAt": x["publishedAt"], "views": x.get("viewsCount") or 0,
                    "likes": x.get("likesCount") or 0, "comments": x.get("commentsCount") or 0,
                    "shares": x.get("sharesCount") or 0,
                    "own": bool(p.get("profile")) and x.get("profileId") == p["profile"],
                })
            offset += 100
            if offset >= total or offset >= 1000:
                break
        meta = {k: p[k] for k in ("slug", "name", "role", "cats")}
        meta["handle"] = next((v["handle"] for v in vids if v["own"]), None)
        meta["totalMatches"] = total or 0
        out["politicians"].append({**meta, "videos": vids})
        print(f"{p['name']:<28} {len(vids):>4} videos ({sum(v['own'] for v in vids)} own)")
    json.dump(out, open("morena_data.json", "w"), ensure_ascii=False)
    print("wrote morena_data.json")


if __name__ == "__main__":
    main()
