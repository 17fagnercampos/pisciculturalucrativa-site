# Site pisciculturalucrativa.com.br

Página da Piscicultura Lucrativa, hub nacional de pisciculturas. Os textos ficam em arquivos simples e o site é gerado a cada mudança.

## Como editar (sem programar)

1. Entre em **https://app.pagescms.org** com a conta do GitHub.
2. Abra este repositório.
3. No menu da esquerda:
   - **Textos da página**: cada bloco da página, na ordem em que aparece.
   - **Configurações**: número de WhatsApp, logo, redes sociais, Google Analytics e Pixel da Meta.
4. Clique em **Save**. Em 1 a 2 minutos a Cloudflare publica a mudança no ar.

Dica: no texto do topo, palavras entre `*asteriscos*` aparecem em amarelo.

## Onde fica cada coisa

| Arquivo | O que tem |
|---|---|
| `conteudo/site.yml` | Todos os textos da página. |
| `conteudo/config.yml` | WhatsApp, logo, redes, Analytics, Pixel. |
| `build.py` | O gerador do site (layout de cada seção). |
| `assets/site.css` | Visual pronto (Tailwind, o mesmo tema do site antigo). |
| `estilo/` | Configuração do Tailwind. Se mudar classes no `build.py`, rode `npm install && npm run css`. |
| `fonte/logo.png` | Logo oficial em alta. Se trocar, rode `python3 gerar_imagens.py` para refazer ícones e a imagem de compartilhamento. |
| `icones_lucide.py` | Ícones do site (Lucide). |
| `vendor/` | Biblioteca YAML em Python puro, para o build não depender de instalação. |

## Publicação (Cloudflare)

- Comando de build: `python3 build.py`
- Pasta de saída: `dist`
- Domínios: `pisciculturalucrativa.com.br` e `www.pisciculturalucrativa.com.br`
