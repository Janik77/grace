(function(){
  function fmt(n){ if (isNaN(n)||n===null) return '0.00'; return Number(n).toLocaleString('ru-RU',{minimumFractionDigits:2, maximumFractionDigits:2}); }
  function parseNum(v){ if(!v) return 0; v=(''+v).replace(/\s/g,'').replace(/₸/g,'').replace(/,/g,'.'); return parseFloat(v)||0; }

  let customColumns=[]; let rowCount=0;
  const tableBody = document.getElementById('tableBody');
  const subtotalEl = document.getElementById('subtotal');
  const percentEl = document.getElementById('percent');
  const percentAmountEl = document.getElementById('percentAmount');
  const grandTotalEl = document.getElementById('grandTotal');

  function addRow(data={}){
    rowCount++; const tr=document.createElement('tr'); tr.dataset.row=rowCount;
    const tdIndex=document.createElement('td'); tdIndex.textContent=rowCount; tr.appendChild(tdIndex);

    const tdName=document.createElement('td'); const nameInput=document.createElement('input'); nameInput.type='text'; nameInput.className='form-control'; nameInput.placeholder='Материал, услуга…'; nameInput.value=data.name||''; tdName.appendChild(nameInput); tr.appendChild(tdName);
    const tdUnit=document.createElement('td'); const unitInput=document.createElement('input'); unitInput.type='text'; unitInput.className='form-control'; unitInput.placeholder='м² / компл. / шт.'; unitInput.value=data.unit||''; tdUnit.appendChild(unitInput); tr.appendChild(tdUnit);
    const tdQty=document.createElement('td'); const qtyInput=document.createElement('input'); qtyInput.type='number'; qtyInput.step='0.01'; qtyInput.className='form-control input-num'; qtyInput.value=(data.qty!==undefined)?data.qty:''; tdQty.appendChild(qtyInput); tr.appendChild(tdQty);
    const tdPrice=document.createElement('td'); const priceInput=document.createElement('input'); priceInput.type='number'; priceInput.step='0.01'; priceInput.className='form-control input-num'; priceInput.value=(data.price!==undefined)?data.price:''; tdPrice.appendChild(priceInput); tr.appendChild(tdPrice);
    const tdTotal=document.createElement('td'); tdTotal.className='money'; tdTotal.textContent='0.00 ₸'; tr.appendChild(tdTotal);

    customColumns.forEach(col=>{ const td=document.createElement('td'); const inp=document.createElement('input'); inp.type='text'; inp.className='form-control'; td.appendChild(inp); tr.appendChild(td); });

    const tdAct=document.createElement('td'); tdAct.className='text-center'; const delBtn=document.createElement('button'); delBtn.className='btn btn-sm btn-outline-danger'; delBtn.textContent='Удалить'; delBtn.addEventListener('click',()=>{ tr.remove(); recalcAll(); renumber(); }); tdAct.appendChild(delBtn); tr.appendChild(tdAct);

    function updateRow(){ const q=parseNum(qtyInput.value); const p=parseNum(priceInput.value); tdTotal.textContent=fmt(q*p)+' ₸'; recalcAll(); }
    qtyInput.addEventListener('input',updateRow); priceInput.addEventListener('input',updateRow);

    tableBody.appendChild(tr); updateRow();
  }
  function renumber(){ Array.from(tableBody.querySelectorAll('tr')).forEach((tr,idx)=> tr.querySelector('td:first-child').textContent=idx+1 ); }
  function recalcAll(){
    let sum=0; Array.from(tableBody.querySelectorAll('tr')).forEach(tr=>{ const t=tr.querySelector('td:nth-child(6)').textContent || '0'; sum += parseNum(t); });
    subtotalEl.textContent=fmt(sum)+' ₸';
    const pct=parseNum(percentEl.value); const pctAmount=sum*(pct/100); percentAmountEl.textContent=fmt(pctAmount)+' ₸'; grandTotalEl.textContent=fmt(sum+pctAmount)+' ₸';
  }
  percentEl?.addEventListener('input',recalcAll);

  document.getElementById('addRow').addEventListener('click',()=>addRow());
  document.getElementById('addColumn').addEventListener('click',()=>{ const name=prompt('Название колонки:'); if(!name) return; const headerRow=document.getElementById('headerRow'); const actionTh=headerRow.querySelector('th:last-child'); const th=document.createElement('th'); th.className='custom-col-header'; th.textContent=name; headerRow.insertBefore(th,actionTh); Array.from(tableBody.querySelectorAll('tr')).forEach(tr=>{ const td=document.createElement('td'); const inp=document.createElement('input'); inp.type='text'; inp.className='form-control'; td.appendChild(inp); tr.insertBefore(td, tr.querySelector('td:last-child')); }); });
  document.getElementById('resetColumns').addEventListener('click',()=>{ const headerRow=document.getElementById('headerRow'); const ths=Array.from(headerRow.children); if(ths.length>7){ for(let i=ths.length-2;i>=6;i--) headerRow.removeChild(ths[i]); } Array.from(tableBody.querySelectorAll('tr')).forEach(tr=>{ const tds=Array.from(tr.children); if(tds.length>7){ for(let i=tds.length-2;i>=6;i--) tr.removeChild(tds[i]); } }); });

  function exportCSV(){
    const rows=[]; const ths=Array.from(document.querySelectorAll('#headerRow th')).map(th=>th.textContent.trim()); ths.pop(); rows.push(ths);
   const percent = document.getElementById('percent').value || 0;
const percentAmount = document.getElementById('percentAmount').innerText;
const grandTotal = document.getElementById('grandTotal').innerText;

rows.push(["Процент (%)", percent]);
rows.push(["Сумма по проценту", percentAmount]);
rows.push(["Итоговая сумма", grandTotal]);

const csv = '\uFEFF' + rows.map(r => r.join(';')).join('\n');
const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
const url = URL.createObjectURL(blob);
  }
  function copyForWord(){
  const table=document.getElementById('calcTable');
  let html="<table border='1' cellspacing='0' cellpadding='5'>";
  const headers=table.querySelectorAll('#headerRow th');
  const rows=table.querySelectorAll('tr');
  headers.forEach((th,i)=>{ if(i===headers.length-1) return; html+="<th>"+th.innerText+"</th>"; });
  rows.forEach(tr=>{
    html+="<tr>";
    const cells=tr.querySelectorAll('td');
    cells.forEach((td,i)=>{
      if(i===cells.length-1) return;
      html+="<td>"+td.innerText+"</td>";
    });
    html+="</tr>";
  });
  const percent=document.getElementById('percentAmount').innerText;
  const grandTotal=document.getElementById('grandTotal').innerText;
  html+="<tr><td colspan='5'>Процент (%)</td><td>"+percent+"%</td></tr>";
  html+="<tr><td colspan='5'>Сумма по проценту</td><td>"+percentAmount+"</td></tr>";
  html+="<tr><td colspan='5'><b>Итоговая сумма</b></td><td><b>"+grandTotal+"</b></td></tr>";
  html+="</table>";

  // вот здесь стояла ошибка — сейчас исправлено
  const blobInput = new Blob([html], { type: 'text/html' });
  navigator.clipboard.write([new ClipboardItem({ "text/html": blobInput })])
    .then(() => alert('Таблица скопирована! Вставьте в Word (Ctrl+V).'))
    .catch(err => alert('Ошибка копирования: '+err));
}


  document.getElementById('exportCsv').addEventListener('click',exportCSV);
  document.getElementById('copyWord').addEventListener('click',copyForWord);
  document.getElementById('clearAll').addEventListener('click',()=>{ if(!confirm('Очистить все строки и заметки?')) return; document.getElementById('tableBody').innerHTML=''; document.getElementById('notes').value=''; rowCount=0; recalcAll(); });
  document.getElementById('sendTrello').addEventListener('click',()=>window.TrelloSender && window.TrelloSender.send((()=>{ const rows=[]; Array.from(tableBody.querySelectorAll('tr')).forEach(tr=>{ const tds=Array.from(tr.children); rows.push({ index: tds[0].innerText.trim(), name: tds[1].querySelector('input')?.value||'', unit: tds[2].querySelector('input')?.value||'', qty: tds[3].querySelector('input')?.value||'', price: tds[4].querySelector('input')?.value||'', total: tds[5].innerText.replace('₸','').trim()}); }); const notes=document.getElementById('notes').value||''; const percent=document.getElementById('percent').value||'0'; const percentAmount=document.getElementById('percentAmount').innerText||'0'; const grandTotal=document.getElementById('grandTotal').innerText||'0'; const project=document.getElementById('projectName')?.value?.trim()||'Проект без названия'; return {project, rows, notes, percent, percentAmount, grandTotal}; })()));
  document.getElementById('sendSheets').addEventListener('click',()=>window.SheetsSender && window.SheetsSender.send((()=>{ const rows=[]; Array.from(tableBody.querySelectorAll('tr')).forEach(tr=>{ const tds=Array.from(tr.children); rows.push({ index: tds[0].innerText.trim(), name: tds[1].querySelector('input')?.value||'', unit: tds[2].querySelector('input')?.value||'', qty: tds[3].querySelector('input')?.value||'', price: tds[4].querySelector('input')?.value||'', total: tds[5].innerText.replace('₸','').trim()}); }); const notes=document.getElementById('notes').value||''; const percent=document.getElementById('percent').value||'0'; const percentAmount=document.getElementById('percentAmount').innerText||'0'; const grandTotal=document.getElementById('grandTotal').innerText||'0'; const project=document.getElementById('projectName')?.value?.trim()||'Проект без названия'; return {project, rows, notes, percent, percentAmount, grandTotal}; })()));
  addRow({name:'PVC 5–10 мм', unit:'м²'}); addRow({name:'Крепёж / рама', unit:'комплект'}); recalcAll();
})();