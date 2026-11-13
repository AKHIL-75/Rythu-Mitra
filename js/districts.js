window.DISTRICTS={"verified_date": "2026-11-12", "sources": ["https://www.telangana.gov.in/about/districts/", "https://igod.gov.in/sg/AP/E042/organizations"], "Telangana": ["Adilabad", "Bhadradri Kothagudem", "Hanumakonda", "Hyderabad", "Jagtial", "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam", "Kumuram Bheem Asifabad", "Mahabubabad", "Mahabubnagar", "Mancherial", "Medak", "Medchal Malkajgiri", "Mulugu", "Nagarkurnool", "Nalgonda", "Narayanpet", "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy", "Warangal", "Yadadri Bhuvanagiri"], "Andhra Pradesh": ["Alluri Sitharama Raju", "Anakapalli", "Anantapur", "Annamayya", "Bapatla", "Chittoor", "Dr B R Ambedkar Konaseema", "East Godavari", "Eluru", "Guntur", "Kakinada", "Krishna", "Kurnool", "Markapuram", "Nandyal", "NTR", "Palnadu", "Parvathipuram Manyam", "Polavaram", "Prakasam", "SPSR Nellore", "Sri Sathya Sai", "Srikakulam", "Tirupati", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"]};
document.addEventListener('DOMContentLoaded',()=>{
      const select=document.getElementById('city'),input=document.getElementById('custom-city');if(!select||!input)return;
      const list=document.createElement('datalist');list.id='district-list';
      for(const state of ['Telangana','Andhra Pradesh'])for(const name of window.DISTRICTS[state]){
        const o=document.createElement('option');o.value=name;o.label=state;list.append(o);
        const choice=document.createElement('option');choice.value='district:'+name;choice.textContent=name+' — '+state;select.append(choice);
      }
      input.setAttribute('list','district-list');input.placeholder='Search any district or city';input.after(list);
    });
