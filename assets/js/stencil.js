/* Hero "do stencil a pele": para cada tatuagem real do Christian, o stencil roxo e transferido,
   o whip shading assenta a tinta seguindo o fluxo do desenho, o stencil e limpo e a peca fica.
   Cada peca dura PECA s; o ciclo de 3 pecas fecha em 3*PECA s (o MP4 do celular usa o mesmo laco). */
(function (raiz) {
  var PECA = 8.4;
  var VS = 'attribute vec2 p;varying vec2 v;void main(){v=p*.5+.5;v.y=1.-v.y;gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;',
    'varying vec2 v;uniform sampler2D uTex;uniform float uT;uniform vec2 uR;',
    'const vec3 PAPEL=vec3(.925,.914,.890);const vec3 CARVAO=vec3(.071,.067,.071);const vec3 ROXO=vec3(.30,.22,.78);',
    'float h(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}',
    'float ease(float x){x=clamp(x,0.,1.);return x*x*(3.-2.*x);}',
    'vec3 tx(vec2 uv){return vec3(texture2D(uTex,vec2(uv.x/3.,uv.y)).r,texture2D(uTex,vec2((uv.x+1.)/3.,uv.y)).r,texture2D(uTex,vec2((uv.x+2.)/3.,uv.y)).r);}',
    'void main(){',
    ' vec3 d=tx(v);float T=d.x,S=d.y,C=d.z;',
    ' float t=uT;',
    ' float gr=h(floor(v*uR))-.5;',
    /* stencil: transfere de cima para baixo como o papel a ser tirado */
    ' float st=smoothstep(v.y-.08,v.y+.02,ease(t/1.1)*1.12-.04);',
    /* whip shading: cada ponto chega na ordem C, com granulado de agulha na frente */
    ' float s=ease((t-.9)/3.9)*1.12-.06;',
    ' float fr=smoothstep(C-.07,C+.005,s+gr*.05);',
    ' float frente=smoothstep(C-.08,C-.01,s)*(1.-smoothstep(C-.01,C+.03,s));',
    ' float ink=T*fr*smoothstep(.8,1.05,t);',
    ' ink=clamp(ink+T*frente*.18,0.,1.);',
    /* limpeza do stencil depois da sombra */
    ' float limpa=1.-ease((t-4.3)/1.1);',
    ' float stv=S*st*mix(.18,1.,limpa)*(1.-ease((t-5.4)/.5));',
    ' stv*=1.-ink*.55;',
    /* saida: a tinta some pela ordem inversa, em grao */
    ' float sai=ease((t-(' + (PECA - 1.0).toFixed(2) + '))/.95)*1.15;',
    ' ink*=1.-smoothstep(1.-C-.12,1.-C,sai+gr*.08);',
    ' vec3 cor=mix(PAPEL,CARVAO,ink);',
    ' cor=mix(cor,ROXO,stv*.92);',
    ' gl_FragColor=vec4(cor,1.);',
    '}'].join('\n');

  function stencilHero(cv, op) {
    op = op || {};
    var gl = cv.getContext('webgl', { antialias: false, alpha: false, preserveDrawingBuffer: !!op.guardar, powerPreference: 'high-performance' });
    if (!gl) return null;
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
    var U = { t: gl.getUniformLocation(pr, 'uT'), r: gl.getUniformLocation(pr, 'uR'), x: gl.getUniformLocation(pr, 'uTex') };
    gl.uniform1i(U.x, 0);
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
      pronto: function (n) { for (var i = 0; i < n; i++) if (!tex[i]) return false; return true; },
      /* tempo global em s; lado em px CSS */
      desenha: function (tempo, lado, dpr) {
        var n = tex.length || 1, ciclo = PECA * n;
        var tt = ((tempo % ciclo) + ciclo) % ciclo, i = Math.floor(tt / PECA), t = tt - i * PECA;
        var w = Math.round(lado * dpr);
        if (cv.width !== w || cv.height !== w) { cv.width = w; cv.height = w; gl.viewport(0, 0, w, w); }
        gl.bindTexture(gl.TEXTURE_2D, tex[i]);
        gl.uniform1f(U.t, t); gl.uniform2f(U.r, w, w);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        return i;
      }
    };
  }
  raiz.stencilHero = stencilHero;
  raiz.STENCIL_PECA = PECA;
})(this);
