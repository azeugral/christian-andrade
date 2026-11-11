/* Hero "do stencil a pele" (v2). Para cada tatuagem real do Christian:
   0,0-1,3 s  o papel do stencil sai na diagonal e deixa as linhas roxas, com o sangrado da tinta termica
   1,1-5,3 s  o whip shading assenta a tinta pela ordem do desenho; tinta fresca entra mais funda e assenta
   4,9-6,2 s  o stencil e limpo com uma passada larga
   6,2-8,2 s  a peca fica; 8,2-9,0 s a pele volta a ficar limpa
   O shader desenha sobre BRANCO e a pagina aplica mix-blend-mode:multiply: o fundo vira o papel exato
   do site, sem caixa nem emenda (vale para o canvas, o MP4 e o poster). */
(function (raiz) {
  var PECA = 9.0;
  var FASES = [1.25, 5.2];   /* stencil | sombra | pele */
  var VS = 'attribute vec2 p;varying vec2 v;void main(){v=p*.5+.5;v.y=1.-v.y;gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;',
    'varying vec2 v;uniform sampler2D uTex;uniform float uT,uS;uniform vec2 uR;',
    /* cores ja divididas pelo papel #ece9e3, para o multiply devolver carvao #121112 e roxo #4d38c7 */
    'const vec3 TINTA=vec3(.0763,.0730,.0784);const vec3 ROXO=vec3(.3264,.2442,.8806);',
    'float h(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}',
    'float ease(float x){x=clamp(x,0.,1.);return x*x*(3.-2.*x);}',
    'float eo(float x){x=clamp(x,0.,1.);return 1.-pow(1.-x,3.);}',
    'vec4 tx(vec2 uv){return vec4(texture2D(uTex,vec2(uv.x*.25,uv.y)).r,texture2D(uTex,vec2((uv.x+1.)*.25,uv.y)).r,texture2D(uTex,vec2((uv.x+2.)*.25,uv.y)).r,texture2D(uTex,vec2((uv.x+3.)*.25,uv.y)).r);}',
    'void main(){',
    ' vec2 uv=(v-.5)*uS+.5;',
    ' if(uv.x<0.||uv.x>1.||uv.y<0.||uv.y>1.){gl_FragColor=vec4(1.);return;}',
    ' vec4 d=tx(uv);float T=d.x,S=d.y,B=d.z,C=d.w;',
    ' float t=uT;',
    ' vec2 px=floor(gl_FragCoord.xy);float gr=h(px)-.5;float gr2=h(px+17.3)-.5;',
    /* 1. papel do stencil sai na diagonal: frente suave  */
    ' float diag=(uv.x*.42+uv.y*.58);',
    ' float fp=ease((t-.1)/1.25)*1.2-.1;',
    ' float st=smoothstep(diag-.035,diag+.035,fp);',
    /* 2. whip shading: frente granulada que segue C; tinta fresca mais funda que assenta */
    ' float s=ease((t-1.1)/4.2)*1.16-.08;',
    ' float chegou=smoothstep(C-.055,C+.004,s+gr*.045);',
    ' float idade=clamp((s-C)/.16,0.,1.);',
    ' float fresca=(1.-idade)*chegou;',
    ' float ink=T*chegou*(1.+fresca*.30);',
    ' ink+=fresca*T*gr2*.10;',
    /* 3. limpeza do stencil: passada larga no sentido contrario */
    ' float lp=ease((t-4.6)/1.3)*1.3-.15;',
    ' float limpo=smoothstep(1.-diag-.10,1.-diag+.02,lp);',
    ' float stv=(S*.95+B*.22)*st*(1.-limpo);',
    ' stv*=1.-smoothstep(.04,.3,ink);',
    /* 4. saida em grao pela ordem inversa */
    ' float sai=ease((t-' + (PECA - .85).toFixed(2) + ')/.8)*1.2;',
    ' ink*=1.-smoothstep(1.-C-.14,1.-C,sai+gr*.10);',
    ' ink=clamp(ink,0.,1.);',
    ' vec3 cor=mix(vec3(1.),TINTA,ink);',
    ' cor=mix(cor,ROXO,clamp(stv,0.,1.)*.9);',
    ' gl_FragColor=vec4(cor,1.);',
    '}'].join('\n');

  function stencilHero(cv, op) {
    op = op || {};
    var gl = cv.getContext('webgl', { antialias: false, alpha: false, preserveDrawingBuffer: !!op.guardar, powerPreference: 'high-performance' });
    if (!gl) return null;
    var max = gl.getParameter(gl.MAX_TEXTURE_SIZE);
    if (max < 4096) return null;
    function sh(t, s) {
      var o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o);
      if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o));
      return o;
    }
    var pr = gl.createProgram();
    gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(pr); gl.useProgram(pr);
    var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var a = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(a); gl.vertexAttribPointer(a, 2, gl.FLOAT, false, 0, 0);
    var U = { t: gl.getUniformLocation(pr, 'uT'), r: gl.getUniformLocation(pr, 'uR'), s: gl.getUniformLocation(pr, 'uS'), x: gl.getUniformLocation(pr, 'uTex') };
    gl.uniform1i(U.x, 0); gl.uniform1f(U.s, 1);
    gl.clearColor(1, 1, 1, 1);
    var tex = [];
    function textura(i, im) {
      gl.activeTexture(gl.TEXTURE0);
      var t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
      gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.LUMINANCE, gl.LUMINANCE, gl.UNSIGNED_BYTE, im);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      tex[i] = t;
    }
    return {
      textura: textura,
      /* tempo global em s; lado do quadrado em px CSS; devolve {i: peca, f: fase 0..2, p: 0..1 da peca} */
      desenha: function (tempo, lado, dpr) {
        var n = tex.length || 1, ciclo = PECA * n;
        var tt = ((tempo % ciclo) + ciclo) % ciclo, i = Math.floor(tt / PECA), t = tt - i * PECA;
        var w = Math.round(lado * dpr);
        if (cv.width !== w || cv.height !== w) { cv.width = w; cv.height = w; gl.viewport(0, 0, w, w); }
        gl.bindTexture(gl.TEXTURE_2D, tex[i]);
        gl.uniform1f(U.t, t); gl.uniform2f(U.r, w, w);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        return estado(tt);
      }
    };
  }
  function estado(tt) {
    var i = Math.floor(tt / PECA), t = tt - i * PECA;
    return { i: i % 3, f: t < FASES[0] ? 0 : t < FASES[1] ? 1 : 2, p: t / PECA };
  }
  raiz.stencilHero = stencilHero;
  raiz.STENCIL_PECA = PECA;
  raiz.stencilEstado = estado;
})(this);
