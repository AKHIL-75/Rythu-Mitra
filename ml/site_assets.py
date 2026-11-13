"""Small generated browser assets from shared JSON; no duplicated maintained lists."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def build():
    d=json.loads((ROOT/'data/districts.json').read_text(encoding='utf8'))
    text='window.DISTRICTS='+json.dumps(d,ensure_ascii=False)+';\n'
    text+='''document.addEventListener('DOMContentLoaded',()=>{
      const select=document.getElementById('city'),input=document.getElementById('custom-city');if(!select||!input)return;
      const list=document.createElement('datalist');list.id='district-list';
      for(const state of ['Telangana','Andhra Pradesh'])for(const name of window.DISTRICTS[state]){
        const o=document.createElement('option');o.value=name;o.label=state;list.append(o);
        const choice=document.createElement('option');choice.value='district:'+name;choice.textContent=name+' — '+state;select.append(choice);
      }
      input.setAttribute('list','district-list');input.placeholder='Search any district or city';input.after(list);
    });
'''
    (ROOT/'js/districts.js').write_text(text,encoding='utf8')
    p=ROOT/'weather.html';s=p.read_text(encoding='utf8')
    if 'js/districts.js' not in s:s=s.replace('<script defer src="js/app.js"></script>','<script defer src="js/districts.js"></script>\n  <script defer src="js/app.js"></script>')
    p.write_text(s,encoding='utf8')
    p=ROOT/'js/app.js';s=p.read_text(encoding='utf8')
    s=s.replace("$('city').value==='custom'", "($('city').value==='custom'||$('city').value.startsWith('district:'))")
    s=s.replace("$('city').value!=='custom'", "!($('city').value==='custom'||$('city').value.startsWith('district:'))")
    s=s.replace("const query=$('custom-city').value.trim();if(!query)","const query=$('city').value.startsWith('district:')?$('city').value.slice(9):$('custom-city').value.trim();if(!query)")
    s=s.replace("$('custom-city').required=($('city').value==='custom'||$('city').value.startsWith('district:'));", "$('custom-city').required=$('city').value==='custom';")
    s=s.replace('Try a nearby city or choose one from the list.','Some district names do not identify a city. Choose Another city and enter your district headquarters or a nearby town.')
    p.write_text(s,encoding='utf8')

if __name__=='__main__':build()
