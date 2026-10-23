"""Gera o site pisciculturalucrativa.com.br na pasta dist/.

Os textos ficam em conteudo/site.yml e os contatos em conteudo/config.yml.
O visual é o mesmo do site antigo (Tailwind), já pronto em assets/site.css.
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
sys.path.insert(0, str(RAIZ))
import markdown  # noqa: E402
import yaml  # noqa: E402
from icones_lucide import LUCIDE  # noqa: E402

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
EMAIL = str(CFG.get("email") or "").strip()
MSG = S.get("mensagens_whatsapp", {})
VERSAO = date.today().strftime("%Y%m%d")


def e(t):
    return html.escape(str(t or ""), quote=True)


def rico(t, classe):
    """Escapa o texto e transforma *palavras* em destaque."""
    partes = e(t).split("*")
    return "".join(f'<span class="{classe}">{p}</span>' if i % 2 else p for i, p in enumerate(partes))


def paragrafos(t):
    return [" ".join(b.split()) for b in str(t or "").split("\n\n") if b.strip()]


def wa(msg=""):
    return f"https://wa.me/{WA}" + (f"?text={quote(msg)}" if msg else "")


def icone(nome, classe=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'class="lucide lucide-{nome} {classe}" aria-hidden="true">{LUCIDE[nome]}</svg>')


MARCAS = {
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="{c}" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" fill="currentColor" class="{c}" aria-hidden="true"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H8v4h2v8h4v-8h3l1-4h-4V8.5c0-.3.2-.5.5-.5Z"/></svg>',
    "tiktok": '<svg viewBox="0 0 24 24" fill="currentColor" class="{c}" aria-hidden="true"><path d="M16.6 3c.4 2.2 1.8 3.7 4 4v3.2a7.4 7.4 0 0 1-4-1.3v6.6a5.9 5.9 0 1 1-5.9-5.9c.3 0 .6 0 .9.1v3.3a2.7 2.7 0 1 0 1.8 2.5V3h3.2Z"/></svg>',
}
REDES = [(k, n, str(CFG.get(k) or "").strip()) for k, n in
         (("instagram", "Instagram"), ("facebook", "Facebook"), ("tiktok", "TikTok"))]
REDES = [r for r in REDES if r[2]]


def logo_src():
    logo = str(CFG.get("logo") or "").strip()
    return logo if logo else "/assets/logo-112.webp"


# Classes dos botões, iguais às do site antigo
BTN = ("inline-flex items-center justify-center gap-2 whitespace-nowrap ring-offset-background transition-colors "
       "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 "
       "[&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0")
LINK_WA = 'target="_blank" rel="noopener"'


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
        "contactPoint": {"@type": "ContactPoint", "telephone": "+" + WA, "contactType": "sales",
                         "availableLanguage": "Portuguese"},
    }
    if EMAIL:
        dados["email"] = EMAIL
        dados["contactPoint"]["email"] = EMAIL
    if REDES:
        dados["sameAs"] = [u for _, _, u in REDES]
    menu = [("#inicio", "Início"), ("#sobre", "Sobre Nós"), ("#parcerias", "Parcerias"), ("#contato", "Contato")]
    nav_desk = "".join(
        f'<a href="/{h}" class="text-foreground hover:text-primary transition-colors focus:outline-none focus:ring-2 '
        f'focus:ring-primary focus:ring-offset-2 rounded-md px-2 py-1 text-sm xl:text-base">{n}</a>' for h, n in menu)
    nav_cel = "".join(
        f'<a href="/{h}" class="block w-full text-left text-foreground hover:text-primary transition-colors py-2 sm:py-3 '
        f'text-base sm:text-lg focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded-md px-2">{n}</a>'
        for h, n in menu)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<meta name="robots" content="{'index, follow, max-image-preview:large' if indexar else 'noindex'}">
<link rel="canonical" href="{e(url)}">
<meta name="theme-color" content="#0000B3">
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
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/site.css?v={VERSAO}">
<script type="application/ld+json">{json.dumps(dados, ensure_ascii=False)}</script>
{rastreamento()}
</head>
<body>
<a href="#conteudo" class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 bg-primary text-primary-foreground rounded-md px-4 py-2 text-sm font-medium">Pular para o conteúdo principal</a>
<div class="min-h-screen bg-background">
<header class="bg-background border-b border-border sticky top-0 z-50 backdrop-blur-sm bg-background/95" role="banner">
  <div class="container mx-auto px-3 sm:px-4 lg:px-6 py-3 sm:py-4 flex items-center justify-between">
    <a href="/#inicio" class="flex items-center space-x-2 sm:space-x-3" aria-label="{e(NOME)}, início">
      <img src="{e(logo_src())}" alt="Logo Piscicultura Lucrativa - Hub Nacional de Pisciculturas Parceiras" class="h-10 w-10 sm:h-12 sm:w-12 lg:h-14 lg:w-14 rounded-full shadow-lg" width="56" height="56">
      <div class="min-w-0"><div class="text-sm sm:text-base lg:text-xl font-bold text-primary truncate">PISCICULTURA</div><div class="text-xs sm:text-sm text-secondary font-semibold truncate">LUCRATIVA</div></div>
    </a>
    <nav class="hidden lg:flex space-x-6 xl:space-x-8" aria-label="Menu principal">{nav_desk}</nav>
    <a href="{e(wa(MSG.get('geral')))}" {LINK_WA} class="{BTN} text-sm font-medium bg-whatsapp text-whatsapp-foreground hover:bg-whatsapp/90 shadow-lg h-11 rounded-md hidden lg:flex px-4 xl:px-6">{icone("message-circle", "h-4 w-4")}<span class="hidden xl:inline">Falar com Especialista</span><span class="xl:hidden">WhatsApp</span></a>
    <button type="button" id="menu-botao" class="{BTN} rounded-md hover:bg-accent hover:text-accent-foreground lg:hidden h-10 w-10 sm:h-11 sm:w-11" aria-label="Abrir menu" aria-expanded="false" aria-controls="menu-celular">{icone("menu", "icone-abrir h-5 w-5 sm:h-6 sm:w-6")}{icone("x", "icone-fechar hidden h-5 w-5 sm:h-6 sm:w-6")}</button>
  </div>
  <div id="menu-celular" class="lg:hidden bg-background border-t border-border animate-slide-up hidden">
    <div class="container mx-auto px-3 sm:px-4 py-4 space-y-3 sm:space-y-4">
      {nav_cel}
      <a href="{e(wa(MSG.get('geral')))}" {LINK_WA} class="{BTN} text-sm font-medium bg-whatsapp text-whatsapp-foreground hover:bg-whatsapp/90 shadow-lg rounded-md px-8 w-full flex mt-4 sm:mt-6 h-12 sm:h-14">{icone("message-circle", "h-4 w-4 sm:h-5 sm:w-5")}<span class="text-sm sm:text-base">Falar com Especialista</span></a>
    </div>
  </div>
</header>
"""


def rodape():
    so = S.get("rodape", {})
    contato_itens = [
        ("message-circle", "WhatsApp", f'<a href="{e(wa(MSG.get("geral")))}" {LINK_WA} class="text-primary-foreground hover:text-secondary transition-colors">{e(WA_LEG)}</a>'),
        ("phone", "Telefone", f'<a href="tel:+{WA}" class="text-primary-foreground hover:text-secondary transition-colors">{e(WA_LEG)}</a>'),
    ]
    if EMAIL:
        contato_itens.append(("mail", "E-mail", f'<a href="mailto:{e(EMAIL)}" class="text-sm text-primary-foreground hover:text-secondary transition-colors">{e(EMAIL).replace("@", "@<wbr>")}</a>'))
    contato = "".join(
        f'<div class="flex items-center gap-3">{icone(i, "h-5 w-5 text-secondary flex-shrink-0")}<div>'
        f'<p class="text-sm text-primary-foreground/60">{r}</p>{v}</div></div>' for i, r, v in contato_itens)
    redes = ""
    if REDES:
        redes = '<div class="flex gap-3 pt-2">' + "".join(
            f'<a href="{e(u)}" {LINK_WA} aria-label="{n} da {e(NOME)}" class="bg-primary-foreground/10 hover:bg-secondary '
            f'hover:text-primary text-primary-foreground w-10 h-10 rounded-full flex items-center justify-center transition-colors">'
            f'{MARCAS[k].format(c="h-5 w-5")}</a>' for k, n, u in REDES) + "</div>"
    ano = date.today().year
    return f"""
<footer class="bg-primary text-primary-foreground py-16 px-4">
  <div class="container mx-auto max-w-6xl">
    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
      <div class="lg:col-span-2">
        <div class="flex items-center space-x-2 mb-6">
          <img src="{e(logo_src())}" alt="{e(NOME)}" class="h-12 w-12 rounded-full" width="48" height="48" loading="lazy">
          <div><div class="text-xl font-bold">PISCICULTURA</div><div class="text-sm text-secondary font-semibold">LUCRATIVA</div></div>
        </div>
        <p class="text-primary-foreground/80 mb-6 leading-relaxed">{e(so.get("texto"))}</p>
        <a href="{e(wa(MSG.get('geral')))}" {LINK_WA} class="{BTN} rounded-md text-sm font-medium text-primary-foreground shadow-lg h-10 px-4 py-2 bg-secondary hover:bg-secondary/90">{icone("message-circle", "h-4 w-4 mr-2")}Falar com Especialista</a>
      </div>
      <div>
        <h4 class="font-semibold text-lg mb-4 text-secondary">Navegação</h4>
        <ul class="space-y-3">
          <li><a href="#inicio" class="text-primary-foreground/80 hover:text-secondary transition-colors">Início</a></li>
          <li><a href="#sobre" class="text-primary-foreground/80 hover:text-secondary transition-colors">Sobre Nós</a></li>
          <li><a href="#parcerias" class="text-primary-foreground/80 hover:text-secondary transition-colors">Parcerias</a></li>
          <li><a href="#contato" class="text-primary-foreground/80 hover:text-secondary transition-colors">Contato</a></li>
        </ul>
      </div>
      <div>
        <h4 class="font-semibold text-lg mb-4 text-secondary">Contato Direto</h4>
        <div class="space-y-4">{contato}{redes}</div>
      </div>
    </div>
    <div class="border-t border-primary-foreground/20 pt-8">
      <div class="flex flex-col md:flex-row justify-between items-center gap-4">
        <div class="text-center md:text-left">
          <p class="text-primary-foreground/80 text-sm">© {ano} {e(NOME)}. Todos os direitos reservados.</p>
          <p class="text-primary-foreground/60 text-sm">{e(so.get("linha"))}</p>
          <p class="text-sm mt-2"><a href="/politica-de-privacidade" class="text-primary-foreground/80 hover:text-secondary underline-offset-4 hover:underline">Política de Privacidade</a> <span class="text-primary-foreground/40">•</span> <a href="/exclusao-de-dados" class="text-primary-foreground/80 hover:text-secondary underline-offset-4 hover:underline">Exclusão de dados</a></p>
        </div>
        <div class="flex flex-col sm:flex-row items-center gap-4">
          <span class="text-primary-foreground/80 text-sm">Atendimento Nacional</span>
          <a href="{e(wa(MSG.get('geral')))}" {LINK_WA} class="{BTN} text-sm font-medium border bg-background h-9 rounded-md px-3 border-secondary text-secondary hover:bg-secondary hover:text-primary">{icone("message-circle", "h-4 w-4 mr-2")}WhatsApp</a>
        </div>
      </div>
    </div>
  </div>
</footer>
<div class="fixed bottom-6 right-6 z-50">
  <a href="{e(wa(MSG.get('geral')))}" {LINK_WA} aria-label="Conversar no WhatsApp" class="{BTN} bg-whatsapp text-whatsapp-foreground hover:bg-whatsapp/90 rounded-full h-14 w-14 shadow-2xl hover:scale-110 transition-transform animate-pulse">{icone("message-circle", "h-6 w-6")}</a>
</div>
</div>
<script>
(function(){{
  var b=document.getElementById('menu-botao'),m=document.getElementById('menu-celular');
  function alterna(abrir){{
    m.classList.toggle('hidden',!abrir);
    b.setAttribute('aria-expanded',abrir);b.setAttribute('aria-label',abrir?'Fechar menu':'Abrir menu');
    b.querySelector('.icone-abrir').classList.toggle('hidden',abrir);
    b.querySelector('.icone-fechar').classList.toggle('hidden',!abrir);
  }}
  if(b&&m){{
    b.addEventListener('click',function(){{alterna(m.classList.contains('hidden'))}});
    m.querySelectorAll('a').forEach(function(l){{l.addEventListener('click',function(){{alterna(false)}})}});
  }}
  var f=document.getElementById('form-contato');
  if(f){{
    f.addEventListener('submit',function(ev){{
      ev.preventDefault();
      var d=new FormData(f),v=function(k){{return (d.get(k)||'').toString().trim()}};
      var t='Olá, gostaria de entrar em contato através do site:\\n\\n*Nome:* '+v('nome')+'\\n*Email:* '+v('email')+'\\n*Telefone:* '+v('telefone');
      if(v('piscicultura'))t+='\\n*Empresa:* '+v('piscicultura');
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


# Cores de cada cartão (precisam estar escritas por extenso para o Tailwind encontrar)
PILAR_ESTILO = [
    ("target", "border-l-primary", "text-primary"),
    ("eye", "border-l-secondary", "text-secondary"),
    ("heart", "border-l-accent", "text-accent"),
]
MERCADO_ESTILO = [
    "bg-primary text-primary-foreground",
    "bg-secondary text-secondary-foreground",
    "bg-gradient-accent text-white",
]
MODELO_ICONES = ["shield", "dollar-sign", "zap", "users"]
CAMPO = ("flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background "
         "placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring "
         "focus-visible:ring-offset-2 md:text-sm")
ROTULO = "block text-sm font-medium text-primary mb-2"


def pagina_inicial():
    t, so, pa, mo, me, pp, co = (S.get(k, {}) for k in
                                 ("topo", "sobre", "parcerias", "modelo", "mercado", "proximo_passo", "contato"))
    msg_parc, msg_geral = MSG.get("parceria"), MSG.get("geral")

    hist = paragrafos(so.get("historia"))
    historia = "".join(
        f'<p class="text-muted-foreground {"mb-4 sm:mb-6 " if i < len(hist) - 1 else ""}leading-relaxed text-sm sm:text-base lg:text-lg">{rico(p, "text-primary font-semibold")}</p>'
        for i, p in enumerate(hist))

    pilares = ""
    for i, p in enumerate(so.get("pilares") or []):
        ic, borda, cor = PILAR_ESTILO[i % len(PILAR_ESTILO)]
        pilares += (
            f'<div class="rounded-lg border bg-card text-card-foreground shadow-sm border-l-4 {borda} hover:shadow-lg transition-shadow duration-300">'
            f'<div class="p-4 sm:p-6"><div class="flex items-start gap-3 sm:gap-4">{icone(ic, "h-6 w-6 sm:h-8 sm:w-8 flex-shrink-0 mt-1 " + cor)}'
            f'<div><h4 class="font-semibold text-primary mb-2 text-sm sm:text-base lg:text-lg">{e(p.get("titulo"))}</h4>'
            f'<p class="text-muted-foreground text-xs sm:text-sm lg:text-base leading-relaxed">{e(p.get("texto"))}</p></div></div></div></div>')

    vantagens = "".join(
        f'<div class="rounded-lg bg-card text-card-foreground shadow-sm text-center hover:shadow-lg transition-all duration-300 border-2 hover:border-primary/20">'
        f'<div class="p-6"><div class="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">'
        f'{icone(v.get("icone") if v.get("icone") in LUCIDE else "trending-up", "h-8 w-8 text-primary")}</div>'
        f'<h3 class="font-semibold text-primary mb-3">{e(v.get("titulo"))}</h3>'
        f'<p class="text-muted-foreground text-sm">{e(v.get("texto"))}</p></div></div>'
        for v in pa.get("vantagens") or [])

    passos = "".join(
        f'<div class="text-center"><div class="bg-gradient-hero text-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-xl font-bold">{i:02d}</div>'
        f'<h4 class="font-semibold text-primary text-lg mb-4">{e(p.get("titulo"))}</h4>'
        f'<p class="text-muted-foreground leading-relaxed">{e(p.get("texto"))}</p></div>'
        for i, p in enumerate(pa.get("passos") or [], 1))

    itens = "".join(
        f'<div class="flex items-center gap-3">{icone(MODELO_ICONES[i % 4], "h-6 w-6 text-secondary flex-shrink-0")}<span>{e(x)}</span></div>'
        for i, x in enumerate(mo.get("itens") or []))

    mercado = ""
    if me.get("mostrar", True) and me.get("numeros"):
        cards = "".join(
            f'<div class="rounded-lg border shadow-sm {MERCADO_ESTILO[i % 3]}"><div class="p-6 text-center">'
            f'<div class="text-3xl font-bold mb-2">{e(n.get("valor"))}</div><p class="text-sm opacity-90">{e(n.get("rotulo"))}</p></div></div>'
            for i, n in enumerate(me["numeros"]))
        mercado = (f'<div class="text-center mb-16"><h3 class="text-2xl md:text-3xl font-bold text-primary mb-8">{e(me.get("titulo"))}</h3>'
                   f'<div class="grid md:grid-cols-3 gap-6">{cards}</div></div>')

    cartoes = [
        (f'href="{e(wa(msg_geral))}" {LINK_WA}', "bg-whatsapp/10", "message-circle", "text-whatsapp",
         "WhatsApp Principal", WA_LEG, "Atendimento prioritário via WhatsApp"),
        (f'href="tel:+{WA}"', "bg-primary/10", "phone", "text-primary", "Telefone", WA_LEG, CFG.get("horario")),
    ]
    if EMAIL:
        cartoes.append((f'href="mailto:{e(EMAIL)}"', "bg-primary/10", "mail", "text-primary", "E-mail", EMAIL,
                        "Responderemos o quanto antes"))
    cartoes.append((None, "bg-secondary/10", "map-pin", "text-secondary", "Localização", CFG.get("localizacao"),
                    "Atendimento nacional"))
    contato_cards = ""
    for link, fundo, ic, cor, tit, val, sub in cartoes:
        miolo = (f'<div class="p-6"><div class="flex items-center gap-4"><div class="{fundo} p-3 rounded-full flex-shrink-0">{icone(ic, "h-6 w-6 " + cor)}</div>'
                 f'<div class="min-w-0"><h4 class="font-semibold text-primary">{e(tit)}</h4><p class="text-muted-foreground [overflow-wrap:anywhere]">{e(val)}</p>'
                 f'<p class="text-sm text-muted-foreground">{e(sub)}</p></div></div></div>')
        if link:
            contato_cards += f'<a {link} class="block rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-lg transition-shadow">{miolo}</a>'
        else:
            contato_cards += f'<div class="rounded-lg border bg-card text-card-foreground shadow-sm">{miolo}</div>'

    redes = ""
    if REDES:
        redes = ('<div class="rounded-lg border bg-card text-card-foreground shadow-sm mt-6"><div class="p-6 flex items-center justify-between gap-4 flex-wrap">'
                 '<h4 class="font-semibold text-primary">Siga a Piscicultura Lucrativa</h4><div class="flex gap-3">' + "".join(
                     f'<a href="{e(u)}" {LINK_WA} aria-label="{n} da {e(NOME)}" class="bg-primary/10 text-primary hover:bg-primary hover:text-secondary '
                     f'w-11 h-11 rounded-full flex items-center justify-center transition-colors">{MARCAS[k].format(c="h-5 w-5")}</a>'
                     for k, n, u in REDES) + "</div></div></div>")

    corpo = f"""
<main id="conteudo">
<section id="inicio" class="relative bg-gradient-hero text-white py-16 sm:py-20 lg:py-24 px-3 sm:px-4 lg:px-6 text-center overflow-hidden" aria-labelledby="hero-title">
  <div class="container mx-auto max-w-6xl relative z-10">
    <div class="inline-block bg-secondary/20 backdrop-blur-sm rounded-full px-4 sm:px-6 py-2 mb-6 sm:mb-8 animate-fade-in"><span class="text-secondary font-semibold text-sm sm:text-base">{e(t.get("selo"))}</span></div>
    <h1 id="hero-title" class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 sm:mb-6 leading-tight"><span class="text-white block sm:inline">{e(t.get("titulo"))} </span><span class="text-secondary block sm:inline">{e(t.get("titulo_destaque"))}</span></h1>
    <p class="text-lg sm:text-xl md:text-2xl lg:text-3xl mb-6 sm:mb-8 text-white/90 max-w-4xl mx-auto leading-relaxed">{rico(t.get("texto"), "text-secondary font-semibold")}</p>
    <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 lg:gap-6 justify-center items-center mb-8 sm:mb-10 lg:mb-12">
      <a href="{e(wa(msg_parc))}" {LINK_WA} class="{BTN} bg-gradient-cta text-primary-foreground hover:bg-secondary/90 shadow-lg rounded-lg px-10 font-semibold w-full sm:w-auto min-w-48 sm:min-w-52 lg:min-w-56 h-12 sm:h-14 lg:h-16 text-sm sm:text-base lg:text-lg animate-scale-in">{e(t.get("botao_principal"))}</a>
      <a href="{e(wa(msg_geral))}" {LINK_WA} class="{BTN} bg-whatsapp text-whatsapp-foreground hover:bg-whatsapp/90 shadow-lg rounded-lg px-10 font-semibold w-full sm:w-auto flex sm:gap-3 min-w-48 sm:min-w-52 lg:min-w-56 h-12 sm:h-14 lg:h-16 text-sm sm:text-base lg:text-lg animate-scale-in">{icone("message-circle", "h-4 w-4 sm:h-5 sm:w-5 lg:h-6 lg:w-6")}<span class="hidden sm:inline">{e(t.get("botao_whatsapp"))}</span><span class="sm:hidden">WhatsApp</span></a>
    </div>
    <a href="#sobre" class="block w-fit mx-auto animate-bounce" aria-label="Ir para Sobre">{icone("arrow-down", "h-5 w-5 sm:h-6 sm:w-6 lg:h-8 lg:w-8 mx-auto text-secondary")}</a>
  </div>
  <div class="absolute inset-0 opacity-10" aria-hidden="true">
    <div class="absolute top-20 left-10 w-32 h-32 bg-secondary rounded-full blur-3xl"></div>
    <div class="absolute bottom-20 right-10 w-40 h-40 bg-primary rounded-full blur-3xl"></div>
  </div>
</section>

<section id="sobre" class="py-16 sm:py-20 lg:py-24 px-3 sm:px-4 lg:px-6 bg-muted/30">
  <div class="container mx-auto max-w-6xl">
    <div class="text-center mb-12 sm:mb-16 lg:mb-20">
      <h2 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold text-primary mb-4 sm:mb-6 leading-tight">{e(so.get("titulo"))}</h2>
      <p class="text-lg sm:text-xl lg:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">{rico(so.get("subtitulo"), "text-primary font-semibold")}</p>
    </div>
    <div class="grid lg:grid-cols-2 gap-8 lg:gap-12 xl:gap-16 items-center mb-12 sm:mb-16 lg:mb-20">
      <div class="order-2 lg:order-1">
        <h3 class="text-xl sm:text-2xl lg:text-3xl font-bold text-primary mb-4 sm:mb-6">{e(so.get("historia_titulo"))}</h3>
        {historia}
      </div>
      <div class="space-y-4 sm:space-y-6 order-1 lg:order-2">{pilares}</div>
    </div>
    <div class="bg-gradient-accent rounded-2xl p-6 sm:p-8 lg:p-10 text-center text-white">
      <h3 class="text-xl sm:text-2xl lg:text-3xl font-bold mb-4 sm:mb-6">{e(so.get("chamada_titulo"))}</h3>
      <p class="text-white/90 mb-6 sm:mb-8 max-w-2xl mx-auto text-sm sm:text-base lg:text-lg leading-relaxed">{e(so.get("chamada_texto"))}</p>
      <a href="{e(wa(msg_geral))}" {LINK_WA} class="{BTN} text-primary-foreground shadow-lg rounded-lg font-semibold bg-secondary hover:bg-secondary/90 w-full sm:w-auto h-12 sm:h-14 lg:h-16 text-sm sm:text-base lg:text-lg px-6 sm:px-8 lg:px-10">{icone("message-circle", "h-4 w-4 sm:h-5 sm:w-5 mr-2 sm:mr-3")}{e(so.get("chamada_botao"))}</a>
    </div>
  </div>
</section>

<section id="parcerias" class="py-20 px-4 bg-background">
  <div class="container mx-auto max-w-6xl">
    <div class="text-center mb-16">
      <div class="inline-block bg-primary/10 rounded-full px-6 py-2 mb-6"><span class="text-primary font-semibold">{e(pa.get("selo"))}</span></div>
      <h2 class="text-3xl md:text-5xl font-bold text-primary mb-6">{e(pa.get("titulo"))}</h2>
      <p class="text-xl text-muted-foreground max-w-4xl mx-auto">{e(pa.get("subtitulo"))}</p>
    </div>
    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">{vantagens}</div>
    <div class="bg-muted/30 rounded-2xl p-8 mb-20">
      <h3 class="text-2xl md:text-3xl font-bold text-primary text-center mb-12">{e(pa.get("passos_titulo"))}</h3>
      <div class="grid md:grid-cols-3 gap-8">{passos}</div>
    </div>
    <div class="bg-gradient-accent rounded-2xl p-8 text-white mb-20">
      <div class="grid md:grid-cols-2 gap-8 items-center">
        <div>
          <h3 class="text-2xl font-bold mb-4">{e(mo.get("titulo"))}</h3>
          <div class="space-y-4">{itens}</div>
        </div>
        <div class="text-center">
          <div class="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-6">
            <div class="text-4xl font-bold text-secondary mb-2">{e(mo.get("numero"))}</div>
            <div class="text-white/90">{e(mo.get("numero_rotulo"))}</div>
            <div class="text-sm text-white/70 mt-2">{e(mo.get("numero_detalhe"))}</div>
          </div>
          <p class="text-white/90 text-sm">{e(mo.get("frase"))}</p>
        </div>
      </div>
    </div>
    {mercado}
    <div class="bg-gradient-hero rounded-2xl p-8 text-center text-white">
      <h3 class="text-2xl md:text-3xl font-bold mb-4">{e(pp.get("titulo"))}</h3>
      <p class="text-xl text-white/90 mb-8 max-w-3xl mx-auto">{e(pp.get("texto"))}</p>
      <div class="flex flex-col md:flex-row gap-4 justify-center">
        <a href="{e(wa(msg_parc))}" {LINK_WA} class="{BTN} text-primary-foreground shadow-lg h-14 rounded-lg px-10 text-base font-semibold bg-secondary hover:bg-secondary/90">{icone("message-circle", "h-5 w-5 mr-3")}{e(pp.get("botao"))}</a>
      </div>
    </div>
  </div>
</section>

<section id="contato" class="py-20 px-4 bg-muted/30">
  <div class="container mx-auto max-w-6xl">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-5xl font-bold text-primary mb-6">{e(co.get("titulo"))}</h2>
      <p class="text-xl text-muted-foreground max-w-3xl mx-auto">{e(co.get("subtitulo"))}</p>
    </div>
    <div class="grid lg:grid-cols-2 gap-12">
      <div class="min-w-0">
        <h3 class="text-2xl font-bold text-primary mb-8">{e(co.get("coluna_titulo"))}</h3>
        <div class="space-y-6 mb-8">{contato_cards}</div>
        <a href="{e(wa(msg_geral))}" {LINK_WA} class="{BTN} bg-whatsapp text-whatsapp-foreground hover:bg-whatsapp/90 shadow-lg h-14 rounded-lg px-10 text-base font-semibold w-full">{icone("message-circle", "h-5 w-5 mr-3")}{e(co.get("botao_whatsapp"))}</a>
        {redes}
      </div>
      <div class="rounded-lg border bg-card text-card-foreground shadow-sm self-start">
        <div class="flex flex-col space-y-1.5 p-6">
          <h3 class="font-semibold tracking-tight text-2xl text-primary">{e(co.get("form_titulo"))}</h3>
          <p class="text-muted-foreground">{e(co.get("form_texto"))}</p>
        </div>
        <div class="p-6 pt-0">
          <form id="form-contato" class="space-y-6">
            <div class="grid md:grid-cols-2 gap-4">
              <div><label for="f-nome" class="{ROTULO}">Nome Completo *</label><input id="f-nome" name="nome" required autocomplete="name" placeholder="Seu nome completo" class="{CAMPO}"></div>
              <div><label for="f-tel" class="{ROTULO}">Telefone/WhatsApp *</label><input id="f-tel" name="telefone" type="tel" inputmode="tel" required autocomplete="tel" placeholder="(00) 00000-0000" class="{CAMPO}"></div>
            </div>
            <div class="grid md:grid-cols-2 gap-4">
              <div><label for="f-email" class="{ROTULO}">E-mail *</label><input id="f-email" name="email" type="email" required autocomplete="email" placeholder="seu@email.com" class="{CAMPO}"></div>
              <div><label for="f-pisc" class="{ROTULO}">Nome da Piscicultura</label><input id="f-pisc" name="piscicultura" autocomplete="organization" placeholder="Nome da sua piscicultura" class="{CAMPO}"></div>
            </div>
            <div><label for="f-msg" class="{ROTULO}">Mensagem</label><textarea id="f-msg" name="mensagem" rows="4" placeholder="Conte-nos sobre sua piscicultura e seus objetivos..." class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"></textarea></div>
            <button type="submit" class="{BTN} bg-gradient-cta text-primary-foreground hover:bg-secondary/90 shadow-lg h-14 rounded-lg px-10 text-base font-semibold w-full">{icone("message-circle", "h-5 w-5 mr-3")}{e(co.get("botao_form"))}</button>
          </form>
        </div>
      </div>
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
<section class="relative bg-gradient-hero text-white py-24 px-4 text-center">
  <div class="container mx-auto max-w-3xl">
    <h1 class="text-4xl md:text-6xl font-bold mb-6">Página não <span class="text-secondary">encontrada</span></h1>
    <p class="text-xl text-white/90 mb-8">O endereço que você abriu não existe. Volte para o início ou fale com a gente no WhatsApp.</p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <a href="/" class="{BTN} bg-secondary text-primary-foreground hover:bg-secondary/90 shadow-lg h-14 rounded-lg px-10 text-base font-semibold">Ir para o início</a>
      <a href="{e(wa(MSG.get('geral')))}" {LINK_WA} class="{BTN} bg-whatsapp text-whatsapp-foreground hover:bg-whatsapp/90 shadow-lg h-14 rounded-lg px-10 text-base font-semibold">{icone("message-circle")}WhatsApp</a>
    </div>
  </div>
</section>
</main>"""
    return cabeca(f"Página não encontrada · {NOME}", "Página não encontrada.", DOMINIO + "/", indexar=False) + corpo + rodape()


PAGINAS = ["politica-de-privacidade", "exclusao-de-dados"]
TEXTO = ("max-w-3xl mx-auto text-foreground leading-relaxed text-base sm:text-lg "
         "[&_p]:mb-5 [&_h2]:text-2xl [&_h2]:sm:text-3xl [&_h2]:font-bold [&_h2]:text-primary [&_h2]:mt-12 [&_h2]:mb-4 "
         "[&_ul]:list-disc [&_ul]:pl-6 [&_ul]:mb-5 [&_li]:mb-2 [&_a]:text-primary [&_a]:font-semibold [&_a]:underline "
         "[&_a]:underline-offset-4 [&_a:hover]:text-secondary-foreground")


def ler_pagina(slug):
    bruto = (RAIZ / "conteudo" / "paginas" / f"{slug}.md").read_text(encoding="utf-8")
    meta, corpo = {}, bruto
    if bruto.startswith("---"):
        _, fm, corpo = bruto.split("---", 2)
        meta = yaml.safe_load(fm) or {}
    return meta, markdown.markdown(corpo.strip())


def pagina_texto(slug):
    meta, corpo_html = ler_pagina(slug)
    titulo = meta.get("titulo") or slug
    corpo = f"""
<main id="conteudo">
<section class="bg-gradient-hero text-white py-14 sm:py-16 px-4 text-center">
  <div class="container mx-auto max-w-4xl">
    <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold leading-tight">{e(titulo)}</h1>
  </div>
</section>
<section class="py-12 sm:py-16 px-4 bg-background">
  <div class="container mx-auto">
    <article class="{TEXTO}">{corpo_html}
      <p class="text-sm text-muted-foreground mt-10">Última atualização: {date.today().strftime("%d/%m/%Y")}</p>
    </article>
  </div>
</section>
</main>"""
    return cabeca(f"{titulo} | {NOME}" if NOME not in titulo else titulo, meta.get("descricao") or titulo,
                  f"{DOMINIO}/{slug}") + corpo + rodape()


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
    for slug in PAGINAS:
        (DIST / f"{slug}.html").write_text(pagina_texto(slug), encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
    urls = [DOMINIO + "/"] + [f"{DOMINIO}/{slug}" for slug in PAGINAS]
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8",
    )
    shutil.copy(RAIZ / "assets" / "favicon-32.png", DIST / "favicon.ico")
    print("Site gerado em dist/")


if __name__ == "__main__":
    main()
