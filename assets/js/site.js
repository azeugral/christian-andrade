(function () {
  'use strict';
  var D = document, W = window, html = D.documentElement;
  var LANG = 'pt';
  var NOMES = { pt: ['Woody', 'Escorpião', 'Leão'], en: ['Woody', 'Scorpion', 'Lion'] };
  var CAT = { pet: 1, real: 1, neo: 1, manga: 1, cob: 1 };
  function $(s, r) { return (r || D).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || D).querySelectorAll(s)); }
  function guarda(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function le(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  var calmo = W.matchMedia && W.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- hero ---------- */
  var hero = $('.hero'), arte = $('#arte'), poster = $('#arte-poster'), legNome = $('#arte-nome');
  var pecaAtual = 0, faseAtual = 2, lis = $$('#arte-fases li'), barra = $('#arte-barra');
  if (barra) barra.style.transform = 'scaleX(1)';
  function estado(e) {
    mudaPeca(e.i);
    if (e.f !== faseAtual) { faseAtual = e.f; lis.forEach(function (l, k) { l.classList.toggle('on', k === e.f); }); }
    barra.style.transform = 'scaleX(' + e.p.toFixed(4) + ')';
  }
  function forma() {
    var w = html.clientWidth, h = W.innerHeight;
    hero.classList.toggle('pe', w < 760 || w / h < 1.05);
  }
  forma();
  W.addEventListener('resize', forma);
  function mudaPeca(i) {
    if (i === pecaAtual) return;
    pecaAtual = i; legNome.textContent = NOMES[LANG][i];
  }
  var visivel = true;
  if ('IntersectionObserver' in W) new IntersectionObserver(function (e) { visivel = e[0].isIntersecting; }, { threshold: 0 }).observe(hero);

  function comecaShader() {
    var cv = D.createElement('canvas'); cv.setAttribute('aria-hidden', 'true');
    var H = W.stencilHero && W.stencilHero(cv);
    if (!H) return false;
    var nomes = ['cao', 'escorpiao', 'leao'], n = 0;
    nomes.forEach(function (nm, i) {
      var im = new Image(); im.decoding = 'async';
      im.onload = function () {
        H.textura(i, im); n++;
        if (n === nomes.length) roda();
      };
      im.src = 'assets/hero/' + nm + '.webp?v=2';
    });
    var t0 = null, tPausa = 0, ultimo = 0;
    function roda() {
      arte.insertBefore(cv, poster);
      function quadro(ts) {
        requestAnimationFrame(quadro);
        if (!visivel || D.hidden) { if (t0 !== null) tPausa = ts - t0; t0 = null; return; }
        if (t0 === null) t0 = ts - tPausa;
        var lado = arte.clientWidth;
        estado(H.desenha((ts - t0) / 1000, lado, Math.min(W.devicePixelRatio || 1, 2)));
        if (!ultimo) { ultimo = 1; poster.style.opacity = '0'; }
      }
      requestAnimationFrame(quadro);
    }
    return true;
  }
  function comecaVideo() {
    var v = D.createElement('video');
    v.muted = true; v.loop = true; v.playsInline = true; v.autoplay = true;
    v.setAttribute('muted', ''); v.setAttribute('playsinline', ''); v.setAttribute('aria-hidden', 'true');
    v.preload = 'auto'; v.poster = poster.src; v.disablePictureInPicture = true;
    v.src = 'assets/video/hero.mp4?v=2';
    arte.insertBefore(v, poster);
    var ok = false;
    function falha() { if (ok) return; v.remove(); comecaShader(); }
    var p = v.play();
    if (p && p.then) p.then(function () { ok = true; poster.style.opacity = '0'; }).catch(falha);
    v.addEventListener('error', falha);
    (function segue() {
      requestAnimationFrame(segue);
      if (ok && !v.paused) estado(W.stencilEstado(v.currentTime));
    })();
    if ('IntersectionObserver' in W) new IntersectionObserver(function (e) { if (!ok) return; e[0].isIntersecting ? v.play().catch(function () {}) : v.pause(); }).observe(hero);
  }
  if (!calmo) {
    var toque = W.matchMedia && W.matchMedia('(pointer:coarse)').matches;
    if (toque || html.clientWidth < 760) comecaVideo(); else if (!comecaShader()) {}
  }

  /* ---------- topo e menu ---------- */
  var topo = $('#topo');
  function rola() { topo.classList.toggle('rolou', W.scrollY > 10); }
  W.addEventListener('scroll', rola, { passive: true }); rola();
  var bMenu = $('.abre-menu'), menu = $('#menu');
  function fechaMenu() { menu.hidden = true; bMenu.setAttribute('aria-expanded', 'false'); D.body.style.overflow = ''; }
  bMenu.addEventListener('click', function () {
    var abre = menu.hidden; menu.hidden = !abre; bMenu.setAttribute('aria-expanded', String(abre));
    D.body.style.overflow = abre ? 'hidden' : '';
  });
  $$('a', menu).forEach(function (a) { a.addEventListener('click', fechaMenu); });
  W.addEventListener('resize', function () { if (html.clientWidth > 980 && !menu.hidden) fechaMenu(); });

  /* ---------- trabalhos ---------- */
  var grade = $('#grade'), verMais = $('#ver-mais'), filtro = 'todos', limite = 12;
  var PORT = W.PORT || [];
  function lista() { return PORT.filter(function (p) { return filtro === 'todos' || p.cat === filtro; }); }
  function pinta() {
    var l = lista();
    grade.innerHTML = '';
    l.slice(0, limite).forEach(function (p) {
      var b = D.createElement('button'); b.type = 'button'; b.className = 'peca';
      b.setAttribute('aria-label', (LANG === 'en' ? 'Open ' : 'Abrir ') + p[LANG]);
      b.innerHTML = '<img src="assets/img/p/' + p.id + '.webp" alt="' + p[LANG].replace(/"/g, '&quot;') + '" width="720" height="900" loading="lazy" draggable="false"><span class="leg">' + p[LANG] + '</span>' + (p.g.length > 1 ? '<span class="n">1/' + p.g.length + '</span>' : '');
      b.addEventListener('click', function () { abreLb(p.g.map(function (g) { return { src: 'assets/img/g/' + g[0] + '.webp', leg: p[LANG] }; }), 0); });
      grade.appendChild(b);
    });
    verMais.hidden = l.length <= limite;
  }
  $$('.filtros button').forEach(function (b) {
    b.addEventListener('click', function () {
      filtro = b.dataset.f; limite = 12;
      $$('.filtros button').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      pinta();
    });
  });
  verMais.addEventListener('click', function () { limite += 12; pinta(); });

  /* ---------- lightbox ---------- */
  var lb = $('#lb'), lbImg = $('#lb-img'), lbLeg = $('#lb-leg'), fotos = [], fi = 0, focoAntes = null;
  function mostra() {
    var f = fotos[fi];
    lbImg.src = f.src; lbImg.alt = f.leg;
    lbLeg.innerHTML = f.leg + (fotos.length > 1 ? '<span>' + (fi + 1) + ' / ' + fotos.length + '</span>' : '');
    $$('.seta', lb).forEach(function (s) { s.hidden = fotos.length < 2; });
  }
  function abreLb(f, i) { focoAntes = D.activeElement; fotos = f; fi = i; mostra(); lb.hidden = false; D.body.style.overflow = 'hidden'; $('.fecha', lb).focus(); }
  function fechaLb() { lb.hidden = true; D.body.style.overflow = ''; lbImg.src = 'data:,'; if (focoAntes) focoAntes.focus(); }
  function passa(d) { fi = (fi + d + fotos.length) % fotos.length; mostra(); }
  $('.fecha', lb).addEventListener('click', fechaLb);
  $('.ant', lb).addEventListener('click', function () { passa(-1); });
  $('.prox', lb).addEventListener('click', function () { passa(1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) fechaLb(); });
  D.addEventListener('keydown', function (e) {
    if (lb.hidden) { if (e.key === 'Escape' && !menu.hidden) fechaMenu(); return; }
    if (e.key === 'Escape') fechaLb(); else if (e.key === 'ArrowLeft') passa(-1); else if (e.key === 'ArrowRight') passa(1);
  });
  var x0 = null;
  lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 45 && fotos.length > 1) passa(dx < 0 ? 1 : -1); x0 = null; });
  $$('.mini4 button').forEach(function (b, i, todos) {
    b.addEventListener('click', function () {
      var leg = LANG === 'en' ? 'Travel sleeve' : 'Manga das viagens';
      abreLb(todos.map(function (x) { return { src: 'assets/img/g/' + x.dataset.g + '.webp', leg: leg }; }), i);
    });
  });

  /* ---------- coberturas ---------- */
  $$('.cob').forEach(function (c) {
    var b = $('.troca', c);
    b.addEventListener('click', function () { var on = !c.classList.contains('ver'); c.classList.toggle('ver', on); b.setAttribute('aria-pressed', String(on)); });
  });

  /* ---------- lingua ---------- */
  function trocaLingua(l) {
    LANG = l; html.lang = l === 'en' ? 'en' : 'pt-PT';
    $$('[data-en]').forEach(function (el) {
      if (!el.hasAttribute('data-pt')) el.setAttribute('data-pt', el.innerHTML);
      el.innerHTML = l === 'en' ? el.getAttribute('data-en') : el.getAttribute('data-pt');
    });
    $$('[data-en-ph]').forEach(function (el) {
      if (!el.hasAttribute('data-pt-ph')) el.setAttribute('data-pt-ph', el.placeholder);
      el.placeholder = l === 'en' ? el.getAttribute('data-en-ph') : el.getAttribute('data-pt-ph');
    });
    $$('[data-en-aria]').forEach(function (el) {
      if (!el.hasAttribute('data-pt-aria')) el.setAttribute('data-pt-aria', el.getAttribute('aria-label'));
      el.setAttribute('aria-label', l === 'en' ? el.getAttribute('data-en-aria') : el.getAttribute('data-pt-aria'));
    });
    $$('[data-en-alt]').forEach(function (el) {
      if (!el.hasAttribute('data-pt-alt')) el.setAttribute('data-pt-alt', el.alt);
      el.alt = l === 'en' ? el.getAttribute('data-en-alt') : el.getAttribute('data-pt-alt');
    });
    $$('.lingua button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.lang === l)); });
    var lm = $('#lingua-m'); if (lm) lm.textContent = l === 'en' ? 'PT' : 'EN';
    legNome.textContent = NOMES[l][pecaAtual];
    pinta();
    guarda('ca-lang', l);
  }
  $$('.lingua button').forEach(function (b) { b.addEventListener('click', function () { if (b.dataset.lang !== LANG) trocaLingua(b.dataset.lang); }); });
  $('#lingua-m').addEventListener('click', function () { trocaLingua(LANG === 'en' ? 'pt' : 'en'); });
  var ini = le('ca-lang') || ((navigator.language || 'pt').toLowerCase().indexOf('pt') === 0 ? 'pt' : 'en');
  if (ini === 'en') trocaLingua('en'); else pinta();

  /* ---------- orcamento ---------- */
  var form = $('#form'), aviso = $('#aviso');
  $$('[data-pre="haia"]').forEach(function (a) { a.addEventListener('click', function () { $('#f-onde').selectedIndex = 1; }); });
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var nome = form.nome.value.trim(), ideia = form.ideia.value.trim();
    if (!nome || !ideia) {
      aviso.textContent = LANG === 'en' ? 'Please fill in your name and your idea.' : 'Preenche o teu nome e a tua ideia.';
      (nome ? form.ideia : form.nome).focus(); return;
    }
    aviso.textContent = '';
    var est = $('input[name=estilo]:checked', form);
    var en = LANG === 'en';
    var estilo = est ? (en ? est.dataset.enV : est.value) : '';
    var tam = form.tam.options[form.tam.selectedIndex], onde = form.onde.options[form.onde.selectedIndex];
    var tamT = tam.value ? (en ? tam.getAttribute('data-en') : tam.value) : '';
    var ondeT = en ? onde.getAttribute('data-en') : onde.value;
    var linhas = en
      ? ['Hi Christian! I found you through your website and would like a quote.', '', 'Name: ' + nome, estilo && 'Style: ' + estilo, form.zona.value.trim() && 'Body area: ' + form.zona.value.trim(), tamT && 'Size: ' + tamT, 'Where: ' + ondeT, '', 'Idea: ' + ideia, '', "I'll send my references here."]
      : ['Olá Christian! Vi o teu site e gostava de um orçamento.', '', 'Nome: ' + nome, estilo && 'Estilo: ' + estilo, form.zona.value.trim() && 'Zona do corpo: ' + form.zona.value.trim(), tamT && 'Tamanho: ' + tamT, 'Onde: ' + ondeT, '', 'Ideia: ' + ideia, '', 'Envio as referências aqui.'];
    var txt = linhas.filter(function (x) { return x !== false && x !== ''; }).join('\n').replace('\nIdea', '\n\nIdea').replace('\nIdeia', '\n\nIdeia');
    W.open('https://wa.me/351939480752?text=' + encodeURIComponent(txt), '_blank', 'noopener');
  });

  /* ---------- entrada suave ---------- */
  var rev = $$('.rev');
  if ('IntersectionObserver' in W && !calmo) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('vis'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    rev.forEach(function (r) { io.observe(r); });
  } else rev.forEach(function (r) { r.classList.add('vis'); });
})();
