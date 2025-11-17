document.addEventListener('DOMContentLoaded', function(){
  const steps = Array.from(document.querySelectorAll('.step'));
  const total = steps.length;
  let idx = 0;

  const stepNow = document.getElementById('stepNow');
  const stepTotal = document.getElementById('stepTotal');
  const progressBar = document.getElementById('progressBar');
  if (stepTotal) stepTotal.textContent = total || 0;

  function showStep(i){
    steps.forEach(s=>s.classList.remove('active'));
    if (steps[i]) steps[i].classList.add('active');
    if (stepNow) stepNow.textContent = (i+1);
    if (progressBar) progressBar.style.width = Math.round(((i+1)/total)*100) + '%';
  }
  showStep(idx);

  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  prevBtn && prevBtn.addEventListener('click', ()=>{ if (idx>0){ idx--; showStep(idx); } });
  nextBtn && nextBtn.addEventListener('click', ()=>{ if (idx<total-1){ idx++; showStep(idx); } });

  // --- Мини-калькулятор (шаг 4)
  const tbody = document.querySelector('#w_calc tbody');
  const percentEl = document.getElementById('w_percent');
  const pctAmountEl = document.getElementById('w_percent_amount');
  const grandEl = document.getElementById('w_grand');

  function fmt(n){ if (isNaN(n)||n===null) return '0.00'; return Number(n).toLocaleString('ru-RU',{minimumFractionDigits:2, maximumFractionDigits:2}); }
  function parseNum(v){ if (!v) return 0; v=(''+v).replace(/\s/g,'').replace(/₸/g,'').replace(/,/g,'.'); return parseFloat(v)||0; }

  function addRow(data={}){
    if (!tbody) return;
    const tr = document.createElement('tr');

    const cIndex = document.createElement('td'); cIndex.textContent = (tbody.children.length+1);
    const cName = document.createElement('td'); const inName = document.createElement('input'); inName.className='form-control'; inName.value=data.name||''; cName.appendChild(inName);
    const cUnit = document.createElement('td'); const inUnit = document.createElement('input'); inUnit.className='form-control'; inUnit.value=data.unit||''; cUnit.appendChild(inUnit);
    const cQty  = document.createElement('td'); const inQty = document.createElement('input'); inQty.type='number'; inQty.step='0.01'; inQty.className='form-control input-num'; inQty.value=(data.qty!==undefined)?data.qty:''; cQty.appendChild(inQty);
    const cPrice= document.createElement('td'); const inPrice=document.createElement('input'); inPrice.type='number'; inPrice.step='0.01'; inPrice.className='form-control input-num'; inPrice.value=(data.price!==undefined)?data.price:''; cPrice.appendChild(inPrice);
    const cTotal= document.createElement('td'); cTotal.className='money'; cTotal.textContent='0.00 ₸';
    const cAct  = document.createElement('td'); const btn=document.createElement('button'); btn.className='btn btn-sm btn-outline-danger'; btn.textContent='Удалить';
    btn.addEventListener('click',()=>{ tr.remove(); renumber(); recalc(); });
    cAct.appendChild(btn);

    function update(){ cTotal.textContent = fmt(parseNum(inQty.value)*parseNum(inPrice.value))+' ₸'; recalc(); }
    inQty.addEventListener('input',update);
    inPrice.addEventListener('input',update);

    tr.append(cIndex,cName,cUnit,cQty,cPrice,cTotal,cAct);
    tbody.appendChild(tr);
    update();
  }
  function renumber(){ if (!tbody) return; Array.from(tbody.children).forEach((tr,i)=> tr.children[0].textContent=(i+1)); }
  function recalc(){
    if (!tbody || !pctAmountEl || !grandEl || !percentEl) return;
    let sum=0;
    Array.from(tbody.children).forEach(tr=>{
      const t = tr.children[5].innerText||'0';
      sum += parseNum(t);
    });
    const pct = parseNum(percentEl.value);
    const pctAmount = sum*(pct/100);
    pctAmountEl.textContent = fmt(pctAmount)+' ₸';
    grandEl.textContent = fmt(sum+pctAmount)+' ₸';
  }

  const addRowBtn = document.getElementById('w_add_row');
  const clearCalcBtn = document.getElementById('w_clear_calc');
  addRowBtn && addRowBtn.addEventListener('click',()=>addRow());
  clearCalcBtn && clearCalcBtn.addEventListener('click',()=>{ if(tbody){ tbody.innerHTML=''; recalc(); } });
  percentEl && percentEl.addEventListener('input',recalc);

  // seed rows
  addRow({name:'PVC 5–10 мм', unit:'м²'});
  addRow({name:'Крепёж / рама', unit:'комплект'});

  function g(id){ return (document.getElementById(id)||{}).value||''; }
  function t(id){ const el=document.getElementById(id); return el?el.innerText||'': ''; }

  function collect(){
    const info = { company: g('w_company'), start: g('w_start'), due: g('w_due'), client: g('w_client'), phone: g('w_phone'), manager: g('w_manager') };
    const brief = { purpose: g('w_purpose'), materials: g('w_materials'), colors: g('w_colors'), sizes: g('w_sizes'), tech: g('w_tech'), terms: g('w_terms') };
    const design = { v1: g('w_v1'), v2: g('w_v2'), notes: g('w_notes_client'), final: g('w_final'), designer: g('w_designer'), approve_date: g('w_approve_date') };
    const rows=[];
    if (tbody){
      Array.from(tbody.children).forEach(tr=>{
        rows.push({ index: tr.children[0].innerText.trim(), name: tr.children[1].querySelector('input')?.value||'', unit: tr.children[2].querySelector('input')?.value||'', qty: tr.children[3].querySelector('input')?.value||'', price: tr.children[4].querySelector('input')?.value||'', total: tr.children[5].innerText.replace('₸','').trim() });
      });
    }
    const percent = g('w_percent'); const percentAmount = t('w_percent_amount'); const grand = t('w_grand');
    const prod = { materials: g('w_prod_materials'), tech: g('w_prod_tech'), terms: g('w_prod_terms'), montage: g('w_montage') };
    return {info, brief, design, calc:{rows, percent, percentAmount, grand}, prod};
  }

  function exportCSV(){
    const d = collect(); const rows=[["Раздел","Поле","Значение"]];
    function push(section,obj){ Object.keys(obj).forEach(k=> rows.push([section,k,String(obj[k]).replaceAll('"','""')])) }
    push("Информация", d.info); push("Бриф", d.brief); push("Дизайн", d.design);
    rows.push(["—","—","—"]); rows.push(["Расчет","Колонки","#,Статья,Ед,Кол-во,Цена за ед.,Итого"]);
    d.calc.rows.forEach(r=> rows.push(["Расчет","Позиция", `${r.index},${r.name},${r.unit},${r.qty},${r.price},${r.total}`]));
    rows.push(["Расчет","Процент", d.calc.percent]); rows.push(["Расчет","Сумма по проценту", d.calc.percentAmount]); rows.push(["Расчет","Итог", d.calc.grand]);
    rows.push(["—","—","—"]); push("Цех/Монтаж", d.prod);
    const csv = "\uFEFF"+rows.map(r=>'"'+r.join('","')+'"').join('\n'); const blob=new Blob([csv],{type:'text/csv;charset=utf-8;'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='grace_wizard_export.csv'; a.style.display='none'; document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove();
  }

  function copyWord(){
    const d = collect(); function row(k,v){ return `<tr><td>${k}</td><td>${v||''}</td></tr>`; }
    let html = "<h3>Grace — Заказ</h3>";
    html += "<table border='1' cellspacing='0' cellpadding='6'>";
    html += "<tr><th colspan='2'>Информация</th></tr>";
    html += row("Компания/Заказ", d.info.company);
    html += row("Дата старта", d.info.start);
    html += row("Дата сдачи", d.info.due);
    html += row("Клиент (ФИО)", d.info.client);
    html += row("Телефон", d.info.phone);
    html += row("Менеджер", d.info.manager);
    html += "<tr><th colspan='2'>ТЗ / Бриф</th></tr>";
    html += row("Назначение", d.brief.purpose);
    html += row("Материал", d.brief.materials);
    html += row("Цвета", d.brief.colors);
    html += row("Размеры", d.brief.sizes);
    html += row("Техника/Доступ", d.brief.tech);
    html += row("Сроки", d.brief.terms);
    html += "<tr><th colspan='2'>Дизайн</th></tr>";
    html += row("Версия 1", d.design.v1);
    html += row("Версия 2", d.design.v2);
    html += row("Замечания", d.design.notes);
    html += row("Финальный макет", d.design.final);
    html += row("Дизайнер", d.design.designer);
    html += row("Дата утверждения", d.design.approve_date);
    html += "</table><br>";
    html += "<table border='1' cellspacing='0' cellpadding='6'>";
    html += "<tr><th>#</th><th>Статья</th><th>Ед</th><th>Кол-во</th><th>Цена за ед.</th><th>Итого</th></tr>";
    d.calc.rows.forEach(r=>{ html += `<tr><td>${r.index}</td><td>${r.name}</td><td>${r.unit}</td><td>${r.qty}</td><td>${r.price}</td><td>${r.total}</td></tr>`; });
    html += `<tr><td colspan="5">Процент</td><td>${d.calc.percent} %</td></tr>`;
    html += `<tr><td colspan="5">Сумма по проценту</td><td>${d.calc.percentAmount}</td></tr>`;
    html += `<tr><td colspan="5"><b>Итоговая сумма</b></td><td><b>${d.calc.grand}</b></td></tr>`;
    html += "</table><br>";
    html += "<table border='1' cellspacing='0' cellpadding='6'>";
    html += "<tr><th colspan='2'>Цех / Монтаж — сводка</th></tr>";
    html += row("Материалы", d.prod.materials);
    html += row("Техкарта", d.prod.tech);
    html += row("Сроки по этапам", d.prod.terms);
    html += row("Адрес/условия монтажа", d.prod.montage);
    html += "</table>";
    const blobInput = new Blob([html],{type:'text/html'});
    navigator.clipboard.write([new ClipboardItem({"text/html":blobInput})]).then(()=>alert("Скопировано! Вставьте в Word (Ctrl+V).")).catch(e=>alert("Ошибка копирования: "+e.message));
  }

  function sendTrello(){
    const d = collect();
    const flat = {
      project: d.info.company || 'Заказ Grace',
      notes: [
        `Клиент: ${d.info.client} (${d.info.phone})`,
        `Менеджер: ${d.info.manager}`,
        `Сроки: ${d.info.start} → ${d.info.due}`,
        `Назначение: ${d.brief.purpose}`,
        `Материал: ${d.brief.materials}`,
        `Финальный макет: ${d.design.final}`,
        `Цех/Монтаж: ${d.prod.terms} | ${d.prod.montage}`
      ].join('\\n'),
      rows: d.calc.rows,
      percent: d.calc.percent,
      percentAmount: d.calc.percentAmount,
      grandTotal: d.calc.grand
    };
    if (window.TrelloSender) window.TrelloSender.send(flat);
  }
  function sendSheets(){
    const d = collect();
    const flat = {
      project: d.info.company || 'Заказ Grace',
      notes: [
        `Клиент: ${d.info.client} (${d.info.phone})`,
        `Менеджер: ${d.info.manager}`,
        `Сроки: ${d.info.start} → ${d.info.due}`,
        `Назначение: ${d.brief.purpose}`,
        `Материал: ${d.brief.materials}`,
        `Финальный макет: ${d.design.final}`,
        `Цех/Монтаж: ${d.prod.terms} | ${d.prod.montage}`
      ].join('\\n'),
      rows: d.calc.rows,
      percent: d.calc.percent,
      percentAmount: d.calc.percentAmount,
      grandTotal: d.calc.grand
    };
    if (window.SheetsSender) window.SheetsSender.send(flat);
  }

  const exportBtn = document.getElementById('w_export_csv');
  const copyWordBtn = document.getElementById('w_copy_word');
  const sendTrelloBtn = document.getElementById('w_send_trello');
  const sendSheetsBtn = document.getElementById('w_send_sheets');
  exportBtn && exportBtn.addEventListener('click', exportCSV);
  copyWordBtn && copyWordBtn.addEventListener('click', copyWord);
  sendTrelloBtn && sendTrelloBtn.addEventListener('click', sendTrello);
  sendSheetsBtn && sendSheetsBtn.addEventListener('click', sendSheets);
});