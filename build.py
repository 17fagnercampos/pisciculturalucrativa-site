"""Gera o site pisciculturalucrativa.com.br na pasta dist/.

Os textos ficam em conteudo/site.yml e os contatos em conteudo/config.yml.
Rodar:  python3 build.py
"""
import html
import json
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "vendor"))  # yaml em Python puro, sem instalar nada
import yaml  # noqa: E402

DIST = RAIZ / "dist"


def ler(nome):
    with open(RAIZ / "conteudo" / nome, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


CFG = ler("config.yml")
S = ler("site.yml")
DOMINIO = str(CFG.get("dominio") or "https://pisciculturalucrativa.com.br").rstrip("/")
NOME = CFG.get("nome") or "Piscicultura Lucrativa"
WA = "".join(c for c in str(CFG.get("whatsapp") or "") if c.isdigit())
WA_LEG = CFG.get("whatsapp_legivel") or ""


def e(t):
    return html.escape(str(t or ""), quote=True)


def rico(t):
    """Escapa o texto e transforma *palavras* em destaque amarelo."""
    partes = e(t).split("*")
    out = []
    for i, p in enumerate(partes):
        out.append(f'<span class="destaque">{p}</span>' if i % 2 else p)
    return "".join(out)


def paragrafos(t):
    blocos = [b.strip() for b in str(t or "").split("\n\n") if b.strip()]
    return "\n".join(f"<p>{rico(' '.join(b.split()))}</p>" for b in blocos)


def wa(msg=""):
    url = f"https://wa.me/{WA}"
    return url + (f"?text={quote(msg)}" if msg else "")


ICONES = {
    "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z"/></svg>',
    "grafico": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-6"/><path d="M15 8h5v5"/></svg>',
    "escudo": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3 4 6v6c0 5 3.4 8.3 8 9 4.6-.7 8-4 8-9V6l-8-3Z"/><path d="m9 12 2 2 4-4"/></svg>',
    "relogio": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "rota": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="6" cy="19" r="2.5"/><circle cx="18" cy="5" r="2.5"/><path d="M8.5 19H16a3.5 3.5 0 0 0 0-7H8a3.5 3.5 0 0 1 0-7h7.5"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="currentColor" stroke="none" opacity=".15"/><path d="m7.5 12.5 3 3 6-6.5"/></svg>',
    "telefone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>',
    "local": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    "email": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H8v4h2v8h4v-8h3l1-4h-4V8.5c0-.3.2-.5.5-.5Z"/></svg>',
    "tiktok": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 3c.4 2.2 1.8 3.7 4 4v3.2a7.4 7.4 0 0 1-4-1.3v6.6a5.9 5.9 0 1 1-5.9-5.9c.3 0 .6 0 .9.1v3.3a2.7 2.7 0 1 0 1.8 2.5V3h3.2Z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "trofeu": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4Z"/><path d="M17 6h3a3 3 0 0 1-3 4M7 6H4a3 3 0 0 0 3 4"/></svg>',
}


REDES = [(k, n, str(CFG.get(k) or "").strip()) for k, n in
         (("instagram", "Instagram"), ("facebook", "Facebook"), ("tiktok", "TikTok"))]
REDES = [r for r in REDES if r[2]]
EMAIL = str(CFG.get("email") or "").strip()


def redes_html(classe="redes"):
    if not REDES:
        return ""
    itens = "".join(
        f'<a href="{e(u)}" target="_blank" rel="noopener" aria-label="{n} da {e(NOME)}">{ICONES[k]}</a>'
        for k, n, u in REDES
    )
    return f'<div class="{classe}">{itens}</div>'


def logo_url():
    logo = str(CFG.get("logo") or "").strip()
    return logo if logo else "/assets/logo.svg"


def rastreamento():
    out = []
    ga = str(CFG.get("google_analytics_id") or "").strip()
    if ga:
        out.append(
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={e(ga)}"></script>'
            f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}"
            f"gtag('js',new Date());gtag('config','{e(ga)}');</script>"
        )
    px = str(CFG.get("meta_pixel_id") or "").strip()
    if px:
        out.append(
            "<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?"
            "n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;"
            "n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;"
            "s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script',"
            f"'https://connect.facebook.net/en_US/fbevents.js');fbq('init','{e(px)}');fbq('track','PageView');</script>"
        )
    return "\n".join(out)


def cabeca(titulo, descricao, url, indexar=True):
    dados = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": NOME,
        "url": DOMINIO + "/",
        "logo": DOMINIO + "/assets/logo-512.png",
        "description": descricao,
        "areaServed": "BR",
        "address": {"@type": "PostalAddress", "addressRegion": "RS", "addressCountry": "BR"},
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+" + WA,
            "contactType": "sales",
            "availableLanguage": "Portuguese",
        },
    }
    if EMAIL:
        dados["email"] = EMAIL
        dados["contactPoint"]["email"] = EMAIL
    if REDES:
        dados["sameAs"] = [u for _, _, u in REDES]
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<meta name="robots" content="{'index, follow, max-image-preview:large' if indexar else 'noindex'}">
<link rel="canonical" href="{e(url)}">
<meta name="theme-color" content="#06065F">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{e(NOME)}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{DOMINIO}/assets/og-capa.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/logo.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/site.css?v={VERSAO}">
<script type="application/ld+json">{json.dumps(dados, ensure_ascii=False)}</script>
{rastreamento()}
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo principal</a>
<header class="topo-barra">
  <div class="wrap">
    <a class="marca" href="/#inicio" aria-label="{e(NOME)}, início">
      <img src="{e(logo_url())}" alt="" width="40" height="40">
      <span>PISCICULTURA<small>LUCRATIVA</small></span>
    </a>
    <button class="menu-toggle" aria-label="Abrir menu" aria-expanded="false" aria-controls="menu">{ICONES["menu"]}</button>
    <nav class="menu" id="menu" aria-label="Menu principal">
      <a href="/#sobre">Sobre Nós</a>
      <a href="/#parcerias">Parcerias</a>
      <a href="/#contato">Contato</a>
      <a class="btn btn-wa btn-pequeno" href="{e(wa(S['topo'].get('mensagem_whatsapp')))}" target="_blank" rel="noopener">{ICONES["whatsapp"]} Falar com Especialista</a>
    </nav>
  </div>
</header>
"""


def rodape():
    ano = date.today().year
    return f"""
<footer class="rodape">
  <div class="wrap">
    <a class="marca" href="/#inicio">
      <img src="{e(logo_url())}" alt="" width="40" height="40">
      <span>PISCICULTURA<small>LUCRATIVA</small></span>
    </a>
    <div>© {ano} {e(NOME)} · {e(CFG.get('localizacao'))} · Atendimento nacional<br>
    WhatsApp <a href="{e(wa())}" target="_blank" rel="noopener">{e(WA_LEG)}</a>{f' · <a href="mailto:{e(EMAIL)}">{e(EMAIL)}</a>' if EMAIL else ''}</div>
    {redes_html("redes redes-rodape")}
  </div>
</footer>
<a class="wa-flutuante" href="{e(wa(S['topo'].get('mensagem_whatsapp')))}" target="_blank" rel="noopener" aria-label="Conversar no WhatsApp">{ICONES["whatsapp"]}</a>
<script>
(function(){{
  var b=document.querySelector('.menu-toggle'),m=document.getElementById('menu');
  if(b&&m){{
    b.addEventListener('click',function(){{var a=m.classList.toggle('aberto');b.setAttribute('aria-expanded',a)}});
    m.querySelectorAll('a').forEach(function(l){{l.addEventListener('click',function(){{m.classList.remove('aberto');b.setAttribute('aria-expanded','false')}})}});
  }}
  var f=document.getElementById('form-contato');
  if(f){{
    f.addEventListener('submit',function(ev){{
      ev.preventDefault();
      var d=new FormData(f),v=function(k){{return (d.get(k)||'').toString().trim()}};
      var t='Olá, gostaria de entrar em contato através do site:\\n\\n*Nome:* '+v('nome')+'\\n*Telefone:* '+v('telefone')+'\\n*E-mail:* '+v('email');
      if(v('piscicultura'))t+='\\n*Piscicultura:* '+v('piscicultura');
      if(v('mensagem'))t+='\\n*Mensagem:* '+v('mensagem');
      if(window.fbq)fbq('track','Lead');
      if(window.gtag)gtag('event','generate_lead');
      window.open('https://wa.me/{WA}?text='+encodeURIComponent(t),'_blank','noopener');
    }});
  }}
  document.querySelectorAll('a[href^="https://wa.me"]').forEach(function(a){{
    a.addEventListener('click',function(){{if(window.fbq)fbq('track','Contact');if(window.gtag)gtag('event','contato_whatsapp')}});
  }});
}})();
</script>
</body>
</html>
"""


def pagina_inicial():
    t, so, pa, mo, me, pp, co = (S.get(k, {}) for k in
                                 ("topo", "sobre", "parcerias", "modelo", "mercado", "proximo_passo", "contato"))
    msg_parceria = t.get("mensagem_whatsapp")

    pilares = "".join(
        f'<div class="pilar"><div class="pilar-num">{i}</div><div><h3>{e(p.get("titulo"))}</h3>'
        f'<p>{e(p.get("texto"))}</p></div></div>'
        for i, p in enumerate(so.get("pilares") or [], 1)
    )
    vantagens = "".join(
        f'<div class="vantagem"><div class="icone">{ICONES.get(v.get("icone"), ICONES["check"])}</div>'
        f'<h3>{e(v.get("titulo"))}</h3><p>{e(v.get("texto"))}</p></div>'
        for v in pa.get("vantagens") or []
    )
    passos = "".join(
        f'<div class="passo"><div class="passo-num">{i:02d}</div><h3>{e(p.get("titulo"))}</h3>'
        f'<p>{e(p.get("texto"))}</p></div>'
        for i, p in enumerate(pa.get("passos") or [], 1)
    )
    itens = "".join(f'<li>{ICONES["check"]}<span>{e(i)}</span></li>' for i in mo.get("itens") or [])

    mercado = ""
    if me.get("mostrar", True) and me.get("numeros"):
        nums = "".join(
            f'<div class="numero"><strong>{e(n.get("valor"))}</strong><span>{e(n.get("rotulo"))}</span></div>'
            for n in me["numeros"]
        )
        mercado = f"""
<section class="secao" aria-labelledby="t-mercado">
  <div class="wrap">
    <h2 id="t-mercado" class="centro">{e(me.get("titulo"))}</h2>
    <div class="numeros" style="margin-top:36px">{nums}</div>
  </div>
</section>"""

    corpo = f"""
<main id="conteudo">
<section class="hero" id="inicio">
  <div class="wrap">
    <div class="selo">{ICONES["trofeu"]} {e(t.get("selo"))}</div>
    <h1>{e(t.get("titulo"))} <em>{e(t.get("titulo_destaque"))}</em></h1>
    <p>{rico(t.get("texto"))}</p>
    <div class="hero-botoes">
      <a class="btn btn-amarelo" href="{e(wa(msg_parceria))}" target="_blank" rel="noopener">{e(t.get("botao_principal"))}</a>
      <a class="btn btn-wa" href="{e(wa(msg_parceria))}" target="_blank" rel="noopener">{ICONES["whatsapp"]} {e(t.get("botao_whatsapp"))}</a>
    </div>
  </div>
</section>

<section class="secao" id="sobre" aria-labelledby="t-sobre">
  <div class="wrap">
    <h2 id="t-sobre" class="centro">{e(so.get("titulo"))}</h2>
    <p class="subtitulo centro">{e(so.get("subtitulo"))}</p>
    <div class="sobre-grid">
      <div class="historia"><h3>{e(so.get("historia_titulo"))}</h3>{paragrafos(so.get("historia"))}</div>
      <div class="pilares">{pilares}</div>
    </div>
    <div class="faixa-chamada">
      <div><h3>{e(so.get("chamada_titulo"))}</h3><p>{e(so.get("chamada_texto"))}</p></div>
      <a class="btn btn-amarelo" href="{e(wa(so.get("mensagem_whatsapp")))}" target="_blank" rel="noopener">{e(so.get("chamada_botao"))}</a>
    </div>
  </div>
</section>

<section class="secao parcerias" id="parcerias" aria-labelledby="t-parcerias">
  <div class="wrap">
    <div class="centro"><div class="selo selo-claro">{e(pa.get("selo"))}</div></div>
    <h2 id="t-parcerias" class="centro">{e(pa.get("titulo"))}</h2>
    <p class="subtitulo centro">{e(pa.get("subtitulo"))}</p>
    <div class="vantagens">{vantagens}</div>
    <h2 class="centro" style="margin-bottom:36px">{e(pa.get("passos_titulo"))}</h2>
    <div class="passos">{passos}</div>
  </div>
</section>

<section class="secao" aria-labelledby="t-modelo">
  <div class="wrap">
    <div class="modelo-caixa">
      <div class="modelo-lista">
        <h2 id="t-modelo">{e(mo.get("titulo"))}</h2>
        <ul>{itens}</ul>
        <p class="frase">{e(mo.get("frase"))}</p>
      </div>
      <div class="modelo-numero">
        <strong>{e(mo.get("numero"))}</strong>
        <span>{e(mo.get("numero_rotulo"))}</span>
        <small>{e(mo.get("numero_detalhe"))}</small>
      </div>
    </div>
  </div>
</section>
{mercado}
<section class="secao proximo" aria-labelledby="t-proximo">
  <div class="wrap">
    <h2 id="t-proximo">{e(pp.get("titulo"))}</h2>
    <p>{e(pp.get("texto"))}</p>
    <a class="btn btn-amarelo" href="{e(wa(msg_parceria))}" target="_blank" rel="noopener">{e(pp.get("botao"))}</a>
  </div>
</section>

<section class="secao" id="contato" aria-labelledby="t-contato">
  <div class="wrap">
    <h2 id="t-contato" class="centro">{e(co.get("titulo"))}</h2>
    <p class="subtitulo centro">{e(co.get("subtitulo"))}</p>
    <div class="contato-grid">
      <div class="contato-info">
        <a class="info" href="{e(wa(msg_parceria))}" target="_blank" rel="noopener">
          <div class="icone">{ICONES["whatsapp"]}</div>
          <div><strong>WhatsApp {e(WA_LEG)}</strong><span>Atendimento prioritário pelo WhatsApp</span></div>
        </a>
        <a class="info" href="tel:+{WA}">
          <div class="icone">{ICONES["telefone"]}</div>
          <div><strong>Telefone {e(WA_LEG)}</strong><span>{e(CFG.get("horario"))}</span></div>
        </a>
        {f"""<a class="info" href="mailto:{e(EMAIL)}">
          <div class="icone">{ICONES["email"]}</div>
          <div><strong>{e(EMAIL)}</strong><span>Responderemos o quanto antes</span></div>
        </a>""" if EMAIL else ""}
        <div class="info">
          <div class="icone">{ICONES["local"]}</div>
          <div><strong>{e(CFG.get("localizacao"))}</strong><span>Atendimento em todo o Brasil</span></div>
        </div>
        <a class="btn btn-wa" href="{e(wa(msg_parceria))}" target="_blank" rel="noopener">{ICONES["whatsapp"]} Conversar Agora no WhatsApp</a>
        {f'<div class="siga"><span>Siga a gente</span>{redes_html()}</div>' if REDES else ""}
      </div>
      <form class="form" id="form-contato">
        <h3>{e(co.get("form_titulo"))}</h3>
        <p>{e(co.get("form_texto"))}</p>
        <div class="campo"><label for="f-nome">Nome completo *</label><input id="f-nome" name="nome" required autocomplete="name"></div>
        <div class="duas">
          <div class="campo"><label for="f-tel">Telefone/WhatsApp *</label><input id="f-tel" name="telefone" type="tel" required autocomplete="tel" inputmode="tel"></div>
          <div class="campo"><label for="f-email">E-mail *</label><input id="f-email" name="email" type="email" required autocomplete="email"></div>
        </div>
        <div class="campo"><label for="f-pisc">Nome da piscicultura</label><input id="f-pisc" name="piscicultura" autocomplete="organization"></div>
        <div class="campo"><label for="f-msg">Mensagem</label><textarea id="f-msg" name="mensagem"></textarea></div>
        <button class="btn btn-wa" type="submit">{ICONES["whatsapp"]} {e(co.get("botao_form"))}</button>
      </form>
    </div>
  </div>
</section>
</main>
"""
    seo = S.get("seo", {})
    return cabeca(seo.get("titulo"), seo.get("descricao"), DOMINIO + "/") + corpo + rodape()


def pagina_404():
    corpo = f"""
<main id="conteudo">
<section class="hero"><div class="wrap">
  <h1>Página não <em>encontrada</em></h1>
  <p>O endereço que você abriu não existe. Volte para o início ou fale com a gente no WhatsApp.</p>
  <div class="hero-botoes">
    <a class="btn btn-amarelo" href="/">Ir para o início</a>
    <a class="btn btn-wa" href="{e(wa())}" target="_blank" rel="noopener">{ICONES["whatsapp"]} WhatsApp</a>
  </div>
</div></section>
</main>"""
    return cabeca(f"Página não encontrada · {NOME}", "Página não encontrada.", DOMINIO + "/", indexar=False) + corpo + rodape()


VERSAO = date.today().strftime("%Y%m%d")


def main():
    if not WA:
        sys.exit("Falta o número de WhatsApp em conteudo/config.yml")
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(RAIZ / "assets", DIST / "assets")
    if (RAIZ / "fotos").exists():
        shutil.copytree(RAIZ / "fotos", DIST / "fotos")
    (DIST / "index.html").write_text(pagina_inicial(), encoding="utf-8")
    (DIST / "404.html").write_text(pagina_404(), encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{DOMINIO}/</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n"
        "</urlset>\n",
        encoding="utf-8",
    )
    # Ícone padrão que navegadores pedem direto na raiz
    shutil.copy(RAIZ / "assets" / "favicon-32.png", DIST / "favicon.ico")
    print("Site gerado em dist/")


if __name__ == "__main__":
    main()
