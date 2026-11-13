/* Extend the existing guides from the shared catalog. Never invent crop doses. */
(function(){
 'use strict';
 const D=window.AGRI,old=D.crops;
 const nutrientSource='https://www.icar.gov.in/en/icar-crida-hyderabad-organises-awareness-programme-soil-health-management-and-balanced-fertilizer-0';
 const waterSource='https://icar.gov.in/en/crop-science/other-technologies-farmers-prosperity';
 D.diseaseCare.officer={organic:'Observe the affected and healthy plants. Photograph the whole plant, leaf undersides and root zone. Ask your agriculture officer to identify the cause before treatment.',chemical:'Consult your agriculture officer. No pesticide or dose is recommended from this symptom alone.'};
 D.diseaseCare.officer.organicTe='మొక్క మొత్తం, ఆకుల దిగువ భాగం, వేర్ల దగ్గర లక్షణాలను పరిశీలించి చిత్రాలు తీయండి. చికిత్సకు ముందు కారణాన్ని నిర్ధారించడానికి వ్యవసాయ అధికారిని సంప్రదించండి.';
 D.diseaseCare.officer.chemicalTe='మీ వ్యవసాయ అధికారిని సంప్రదించండి. ఈ లక్షణం ఆధారంగా మాత్రమే పురుగుమందు లేదా మోతాదు సూచించలేదు.';
 for(const c of window.CROP_CATALOG){
   const prior=old[c.id]||{};
   D.crops[c.id]={...prior,en:c.english_name,te:c.telugu_aliases[0],local:c.romanized_aliases[0],
     aliases:[c.english_name.toLowerCase(),...c.english_aliases,...c.romanized_aliases,...c.telugu_aliases],
     category:c.category,water:null,critical:'the stages identified in your local crop schedule',
     tip:'Use root-zone moisture and recent rainfall to decide when to irrigate. Consult your agriculture officer for this crop’s local schedule.',waterSource};
   D.crops[c.id].tipTe='నీరు ఇచ్చే ముందు వేర్ల వద్ద నేల తేమ, ఇటీవలి వర్షం పరిశీలించండి. ఈ పంటకు స్థానిక నీటి ప్రణాళిక కోసం వ్యవసాయ అధికారిని సంప్రదించండి.';
   if(!D.nutrients[c.id])D.nutrients[c.id]={profiles:[],source:nutrientSource,
     note:'Consult your agriculture officer for a soil-test-based nutrient plan. A crop-specific numerical dose has not been verified here.'};
   D.nutrients[c.id].sourceName=D.nutrients[c.id].profiles.length?'TNAU Agritech — crop reference':'ICAR-CRIDA — soil-test-based nutrient planning (general)';
   D.nutrients[c.id].noteTe=D.nutrients[c.id].profiles.length?'ఇది మూల పత్రంలోని ప్రత్యేక పంట పరిస్థితులకు సంబంధించిన సూచన మాత్రమే. మీ నేల, రకం, దశకు అనువైన ఎరువు మోతాదును వ్యవసాయ అధికారితో నిర్ధారించండి.':'భూసార పరీక్ష ఆధారంగా ఎరువుల ప్రణాళిక కోసం వ్యవసాయ అధికారిని సంప్రదించండి. ఈ పంటకు సంఖ్యలతో మోతాదు ఇక్కడ నిర్ధారించలేదు.';
   if(!D.diseases[c.id])D.diseases[c.id]=[
      ['Leaf symptoms — cause unconfirmed','ఆకు లక్షణాలు — కారణం నిర్ధారణ కాలేదు','Spots, yellowing or curled leaves can have several causes. Consult your agriculture officer. This is an inspection cue, not a crop-specific disease diagnosis.',['yellow','spots','curl','powder'],'officer'],
      ['Pest inspection — identify the insect','పురుగుల పరిశీలన','Look for insects, larvae, holes or feeding marks. No pest species is assigned to this crop without identification. Consult your agriculture officer.',['holes'],'officer'],
      ['Root-zone inspection','వేర్ల పరిశీలన','Wilting or soft roots require field inspection. Note wet or dry soil; consult your agriculture officer before treatment.',['wilting','rot'],'officer']];
 }
 // Correct units and avoid transferring a hybrid fertigation schedule to a conventional split.
 D.nutrients.cotton.profiles=[[32,16,16],[48,24,24]].map(row=>row.map(v=>v/.40468564224));
 D.nutrients.cotton.note='TNAU reference: varieties 32:16:16 and hybrids 48:24:24 kg N:P2O5:K2O per acre. The displayed split is an educational allocation; ask for the variety-specific timing.';
 D.nutrients.chilli.profiles=[[60,60,30]];
 D.nutrients.chilli.note='Conventional TNAU reference only: season N:P2O5:K2O = 60:60:30 kg/ha; potassium sulphate is preferred in that source for quality. MOP below is a nutrient-equivalent calculation, not a product prescription.';
 D.nutrients.tomato.profiles=[[200,250,250]];
 D.nutrients.tomato.source='https://agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_fertigation.html';
 D.nutrients.tomato.note='TNAU hybrid drip-fertigation season reference 200:250:250 kg/ha. The product equivalents and three broad rows below do not reproduce the source’s detailed soluble-fertilizer schedule. Confirm locally before use.';
 D.fertilizerNotes.organics=['Count nutrients already supplied by manure. Source: ICAR-CRIDA, balanced soil-test-based nutrient planning. Consult your agriculture officer for manure quality and quantities.'];
 D.fertilizerNotes.split='These broad allocation rows illustrate nutrient accounting and are not a verified crop calendar. If you enter officer-provided amounts, they replace the reference for this calculation; the source link describes the background reference, not your entries. All-basal allocation of manual values is accounting only, not timing advice. An officer must set the actual timing and product choice. Do not repeat amounts already applied.';
 D.fertilizerNotes.intro='Season nutrient equivalents from a cited reference, or from the officer-provided values you entered. Soil test, variety and previous fertilizer must determine the actual dose. Rows illustrate accounting, not a crop calendar.';
 D.water.intro='No universal day interval or water depth is recommended. Use soil moisture, crop stage, rainfall and local advice. Source: ICAR soil-moisture scheduling guidance.';
 D.water.methods.forEach(m=>{m.cost='Get a local quotation';m.saving='Depends on crop, soil and operation';});
 D.water.costNote='No price or percentage saving has been verified for your farm. Consult your agriculture officer and compare local quotations.';
 D.water.tips=['Use a soil-moisture check to decide when to irrigate. Source: ICAR soil-moisture indicator guidance.','Consult your agriculture officer to interpret the crop’s root-zone moisture and irrigation needs.'];
 D.water.paddy='Consult your local rice officer for a field-specific water-management plan.';
 // 22 central MSP commodities, kept explicitly historical. Coconut is shown as processed copra.
 const msp={paddy:2369,jowar:3699,bajra:2775,ragi:4886,maize:2400,red_gram:8000,green_gram:8768,black_gram:7800,cotton:7710,groundnut:7263,sunflower:7721,soybean:5328,sesame:9846,niger:9537,wheat:2425,barley:1980,chickpea:5650,lentil:6700,mustard:5950,safflower:5940,jute:5650,coconut:11582};
 const previous=Object.fromEntries(D.prices.map(p=>[p.crop,p]));
 D.prices=window.CROP_CATALOG.map(c=>({crop:c.id,name:c.english_name+(c.id==='coconut'?' — milling copra, not raw coconut':c.id==='cotton'?' — medium staple':c.id==='jowar'?' — hybrid':c.id==='paddy'?' — common':''),
   sample:previous[c.id]?.sample??null,msp:msp[c.id]??null,
   season:msp[c.id]!==undefined?'Historical 2025-26'+(c.id==='coconut'?' (copra 2025)':''):'No verified MSP reference here; consult your officer',
   source:'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2152556'}));
 D.market.intro='Historical 2025-26 central MSP references: PIB, 5 August 2025, ₹/quintal. Coconut entry is milling copra. Samples are fictional examples, never live prices. No verified reference means ask your officer; it does not assert that no price support exists.';
 D.home.irrigation=['Use soil moisture, recent rainfall and crop stage to decide when to water. Source: ICAR soil-moisture scheduling guidance.','The water guide converts a depth you choose into litres. Consult your agriculture officer for this crop’s actual timing and depth.'];
 D.topics.other_agri={en:'Other farm question',te:'ఇతర వ్యవసాయ ప్రశ్న',icon:'🌱',file:'about.html',description:'Ask your agriculture officer about planting, harvest, storage or equipment.',descriptionTe:'నాట్లు, కోతలు, నిల్వ గురించి వ్యవసాయ అధికారిని సంప్రదించండి.'};
 D.home.other_agri=['Your question may concern planting, harvesting, storage, machinery or another farm topic. Please discuss the details with your agriculture officer.'];
 D.homeCrop.other_agri='{crop}: consult your agriculture officer for this farm topic.';
 D.homeCrop.weather='For {crop}, check the latest local weather warning before field work.';
 D.sourceLinks={nutrientSource,waterSource};
})();

/* Only dated support-price references are displayed; legacy illustrative rates are unused. */
window.AGRI.prices.forEach(p=>delete p.sample);
window.AGRI.market.intro='Historical central MSP references: PIB, 5 August 2025, rupees per quintal. These are not live mandi prices. Where no verified MSP reference is available, consult your agriculture officer or see Agmarknet. Coconut refers to milling copra, not raw coconut.';
