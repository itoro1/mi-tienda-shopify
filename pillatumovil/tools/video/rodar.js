const { chromium } = require('playwright');
const [,, ancho, alto, carpeta, fps, segs] = process.argv;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +ancho, height: +alto } });
  await p.goto('file://' + process.cwd() + '/estudio.html'); await p.waitForTimeout(600);
  const n = +fps * +segs;
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => setT(t), i / n);
    await p.screenshot({ path: `${carpeta}/f${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  console.log(carpeta, n, 'fotogramas'); await b.close();
})();
