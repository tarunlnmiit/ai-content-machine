// GET /get-worksheet?slug=<slug> — renders the email-capture page.
import { resolve } from "./_lib/manifest.mjs";

function esc(s = "") {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[c]);
}

const NICHE_LABEL = {
  data_science_tech: "Data Science",
  life_self_dev: "Life & Self-Development",
  poetry_quotes: "Poetry",
};

function notFoundPage() {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Worksheet not found</title>${STYLE}</head>
<body class="centered"><main class="card">
<p class="kicker">404</p>
<h1>That worksheet isn't here</h1>
<p class="lede">The link may be old or mistyped. Head back to the post and try the download button again.</p>
</main></body></html>`;
}

const STYLE = `<style>
:root{
  --ink: oklch(22% 0.02 270);
  --paper: oklch(97% 0.01 95);
  --accent: oklch(58% 0.17 28);
  --accent-ink: oklch(98% 0.01 95);
  --muted: oklch(48% 0.02 270);
  --line: oklch(88% 0.01 95);
  --ease: cubic-bezier(0.16,1,0.3,1);
}
*{box-sizing:border-box}
body{margin:0;font-family:"Iowan Old Style",Georgia,"Times New Roman",serif;
  color:var(--ink);background:var(--paper);
  background-image:radial-gradient(oklch(0% 0 0/0.04) 1px,transparent 1px);
  background-size:22px 22px;line-height:1.5;-webkit-font-smoothing:antialiased}
.centered{min-height:100dvh;display:grid;place-items:center;padding:2rem}
main.wrap{max-width:46rem;margin:0 auto;padding:clamp(2rem,6vw,5rem) 1.5rem}
.card{max-width:34rem;background:oklch(99% 0.005 95);border:1px solid var(--line);
  border-radius:2px;padding:clamp(1.5rem,5vw,3rem);
  box-shadow:0 1px 0 var(--line),0 24px 60px -30px oklch(0% 0 0/0.35)}
.kicker{font-family:ui-monospace,"SF Mono",Menlo,monospace;text-transform:uppercase;
  letter-spacing:0.22em;font-size:0.7rem;color:var(--accent);margin:0 0 1rem}
h1{font-size:clamp(2rem,1rem+5vw,3.4rem);line-height:1.02;margin:0 0 0.6rem;
  font-weight:600;letter-spacing:-0.02em}
.lede{font-size:1.12rem;color:var(--muted);margin:0 0 2rem;max-width:32rem}
form{display:flex;flex-direction:column;gap:0.75rem;margin:0}
label{font-size:0.85rem;color:var(--muted)}
input[type=email]{font:inherit;font-size:1.05rem;padding:0.85rem 1rem;
  border:1px solid var(--line);border-radius:2px;background:var(--paper);
  transition:border-color .2s var(--ease),box-shadow .2s var(--ease)}
input[type=email]:focus{outline:none;border-color:var(--accent);
  box-shadow:0 0 0 3px oklch(58% 0.17 28/0.18)}
button{font:inherit;font-weight:600;font-size:1.05rem;cursor:pointer;
  padding:0.9rem 1rem;border:none;border-radius:2px;color:var(--accent-ink);
  background:var(--accent);transition:transform .2s var(--ease),filter .2s var(--ease)}
button:hover{filter:brightness(1.06)}
button:active{transform:translateY(1px)}
button[disabled]{opacity:.6;cursor:progress}
.fine{font-size:0.8rem;color:var(--muted);margin:1.1rem 0 0}
.err{color:var(--accent);font-size:0.9rem;min-height:1.2em;margin:0}
.honey{position:absolute;left:-9999px}
</style>`;

export default function handler(req, res) {
  const slug = String(req.query?.slug ?? "");
  const ws = resolve(slug);

  if (!ws) {
    res.statusCode = 404;
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.end(notFoundPage());
    return;
  }

  const niche = NICHE_LABEL[ws.niche] ?? "Companion worksheet";
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(ws.title)} — Worksheet</title>${STYLE}</head>
<body><main class="wrap"><section class="card" aria-labelledby="h">
<p class="kicker">${esc(niche)} · Free worksheet</p>
<h1 id="h">${esc(ws.title)}</h1>
<p class="lede">Drop your email and I'll send you straight to the worksheet. You'll also get new ones as they land — unsubscribe anytime.</p>
<form id="f" method="post" action="/api/subscribe" novalidate>
  <input type="hidden" name="slug" value="${esc(ws.slug)}">
  <input class="honey" type="text" name="company" tabindex="-1" autocomplete="off" aria-hidden="true">
  <label for="email">Email address</label>
  <input id="email" type="email" name="email" required autocomplete="email" placeholder="you@example.com">
  <button type="submit">Send me the worksheet →</button>
  <p class="err" id="err" role="alert"></p>
</form>
<p class="fine">No spam. The worksheet opens right after — check your inbox for more.</p>
</section></main>
<script>
const f=document.getElementById('f'),err=document.getElementById('err'),btn=f.querySelector('button');
f.addEventListener('submit',async(e)=>{
  e.preventDefault();err.textContent='';
  const email=f.email.value.trim();
  if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)){err.textContent='Please enter a valid email.';return;}
  btn.disabled=true;btn.textContent='Sending…';
  try{
    const r=await fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({email,slug:f.slug.value,company:f.company.value})});
    const data=await r.json().catch(()=>({}));
    if(r.ok&&data.url){window.location.href=data.url;return;}
    err.textContent=data.error||'Something went wrong. Try again.';
  }catch{err.textContent='Network error. Try again.';}
  btn.disabled=false;btn.textContent='Send me the worksheet →';
});
</script>
</body></html>`;

  res.statusCode = 200;
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=300");
  res.end(html);
}
