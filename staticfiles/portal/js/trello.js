(function(){
  const TRELLO_KEY='PASTE_YOUR_KEY_HERE';
  const TRELLO_TOKEN='PASTE_YOUR_TOKEN_HERE';
  const LIST_ID='PASTE_YOUR_LIST_ID_HERE';

  async function createCard(data){
    const name='[Grace] '+(data.project||'Без названия');
    const desc=[ `Итог: ${data.grandTotal}`, `Процент: ${data.percent} → ${data.percentAmount}`, '', `Заметки:`, data.notes||'-' ].join('\n');
    const url=`https://api.trello.com/1/cards?key=${encodeURIComponent(TRELLO_KEY)}&token=${encodeURIComponent(TRELLO_TOKEN)}`;
    const form=new FormData(); form.append('idList', LIST_ID); form.append('name', name); form.append('desc', desc); form.append('pos','top');
    const resp=await fetch(url,{method:'POST', body:form}); if(!resp.ok) throw new Error('Ошибка создания карточки'); return resp.json();
  }
  async function addChecklist(cardId, rows){
    const url=`https://api.trello.com/1/cards/${cardId}/checklists?key=${encodeURIComponent(TRELLO_KEY)}&token=${encodeURIComponent(TRELLO_TOKEN)}`;
    const resp=await fetch(url,{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name:'Смета / Позиции'})});
    if(!resp.ok) throw new Error('Ошибка чек-листа'); const chk=await resp.json();
    for (const r of rows){ const item = `${r.name} — ${r.qty} × ${r.price} = ${r.total}`.slice(0,180); const addUrl=`https://api.trello.com/1/checklists/${chk.id}/checkItems?key=${encodeURIComponent(TRELLO_KEY)}&token=${encodeURIComponent(TRELLO_TOKEN)}&name=${encodeURIComponent(item)}`; await fetch(addUrl,{method:'POST'}); }
  }
  window.TrelloSender={ async send(data){ if(String(TRELLO_KEY).includes('PASTE_')){ alert('Заполните TRELLO_KEY/TOKEN/LIST_ID в trello.js'); return; } try{ const card=await createCard(data); await addChecklist(card.id, data.rows); alert('Отправлено в Trello ✓'); }catch(e){ alert('Ошибка Trello: '+e.message); } } };
})();