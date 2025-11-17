(function(){
  const WEBHOOK_URL='PASTE_YOUR_APPS_SCRIPT_WEBAPP_URL_HERE';
  window.SheetsSender={ async send(data){ if(String(WEBHOOK_URL).includes('PASTE_')){ alert('Укажите WEBHOOK_URL в sheets.js'); return; } try{ const resp=await fetch(WEBHOOK_URL,{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)}); if(!resp.ok) throw new Error('HTTP '+resp.status); const json=await resp.json(); if(json && json.ok) alert('Отправлено в Google Sheets ✓'); else alert('Ответ без ok'); }catch(e){ alert('Ошибка Google Sheets: '+e.message); } } };
})();