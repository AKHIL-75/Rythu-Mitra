import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
const build=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(build,'..');
const runtime=path.join(os.homedir(),'.cache','codex-runtimes','codex-primary-runtime','dependencies');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'node','node_modules','@oai','artifact-tool','dist','artifact_tool.mjs')).href);
const skill='C:/Users/akhil/.codex/plugins/cache/openai-primary-runtime/presentations/26.1111.10930/skills/presentations';
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools','artifact_tool_utils.mjs')).href);
const m=JSON.parse(await fs.readFile(path.join(root,'ml/models/metrics.json'),'utf8'));
const reports={};for(const file of ['questions_test_results.json','practical_test_results.json','charts_test_results.json','test_summary.json'])reports[file]=JSON.parse(await fs.readFile(path.join(root,'reports',file),'utf8'));
const browserPass=reports['questions_test_results.json'].passed+reports['practical_test_results.json'].passed+reports['charts_test_results.json'].passed;
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={green:'#1F4D2E',dark:'#143720',gold:'#A36C00',pale:'#F2F5ED',ink:'#20362A',muted:'#526359',white:'#FFFFFF',line:'#D9E3D6'};
const source=(s)=>'Project source: '+path.join(root,s);
const pct=x=>(100*x).toFixed(2)+'%';
const all=[];
function txt(s,text,x,y,w,h,size=27,color=C.ink,bold=false,font='Arial'){
 const box=s.shapes.add({geometry:'textbox',name:text.slice(0,45),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 box.text=text;box.text.style={typeface:font,fontSize:size,color,bold,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};return box;
}
function slide(title,note='',dark=false){const s=p.slides.add();s.background.fill=dark?C.dark:C.pale;all.push(s);if(title)txt(s,title,68,44,1145,82,44,dark?C.white:C.green,true);txt(s,'RYTHU MITRA  /  NLP PROJECT',70,675,900,24,16,dark?'#C7D8C1':C.muted);txt(s,String(all.length).padStart(2,'0'),1160,675,60,24,16,dark?'#C7D8C1':C.muted);s.speakerNotes.text=note;return s;}
function para(s,heading,text,x,y,w=525){txt(s,heading,x,y,w,42,29,C.green,true);txt(s,text,x,y+54,w,130,27);}
function footer(s,text){txt(s,text,70,626,1140,34,18,C.muted);}
async function image(s,name,x,y,w,h){const b=await fs.readFile(path.join(build,name));s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:'Actual Rythu Mitra website: '+name,fit:'contain',position:{left:x,top:y,width:w,height:h}});}
function table(s,headers,rows,widths,{x=70,y=165,h=420,size=24,font='Arial'}={}){
 const vals=[headers,...rows],t=s.tables.add({rows:vals.length,columns:headers.length,left:x,top:y,width:widths.reduce((a,b)=>a+b,0),height:h,columnWidths:widths,values:vals});
 t.borders.assign({style:'solid',fill:C.line,width:1});
 for(let r=0;r<vals.length;r++)for(let c=0;c<headers.length;c++){const cell=t.getCell(r,c);cell.fill=r===0?C.green:r%2?C.white:C.pale;cell.text.style={typeface:font,fontSize:size,bold:r===0||c===0,color:r===0?C.white:C.ink,verticalAlignment:'middle',insets:{left:12,right:10,top:10,bottom:10}};}
 return t;
}

// 1. Minimal title and real product evidence.
{
 const s=slide('',`Opening: introduce the project as an NLP intent classifier with practical advisory workflows. The title uses the known presenter name and a team label because other names were not supplied. Replace that editable line with the final team names before presenting if desired. Sources: ${source('index.html')}; ${source('js/answers.js')}.`,true);
 txt(s,'Rythu Mitra',68,105,1100,100,76,C.white,true);
 txt(s,'Telugu–English Code-Mixed\nAgricultural Query Assistant',70,224,1100,124,48,'#F6D16F');
 txt(s,'Natural Language Processing project\nB.Tech CSE, SR University',72,408,680,90,28,'#DAE6D4');
 txt(s,'Akhil Naragani and team',72,550,1080,55,30,C.white,true);
}
// 2. Problem statement.
{
 const s=slide('Problem statement',`Explain the language mismatch with the sample question, then separate the question's topic from the actual agronomic cause. Holes do not uniquely identify a pest. The system must recognize the crop and symptom and give useful next steps while seeking missing details. The quote is the user's actual test query, not a dataset claim. Sources: ${source('js/practical.js')}; ${source('tests/practical.cjs')}.`);
 txt(s,'Farmers ask in Telugu, English and mixed spellings',70,155,1100,90,36,C.ink,true);
 txt(s,'“na potato chetu ki holes unnay em cheyali”',70,282,1100,75,36,C.gold,true);
 para(s,'Language variation','Romanized Telugu, Telugu script and spelling differences make keyword-only matching brittle.',70,405,520);
 para(s,'An incomplete question','The assistant still needs the affected part and visible symptoms before suggesting treatment.',680,405,520);
}
// 3. Objectives.
{
 const s=slide('Objectives and scope',`Describe the objectives as working system capabilities. Recognition combines trained ML with explicit routing and entity rules. The website does not claim to answer every possible agricultural question. Weather and mandi rates require services, while private payment status and equipment availability remain on official external channels. Sources: ${source('js/requests.js')}; ${source('js/answers.js')}; ${source('js/entities.js')}.`);
 const rows=[['01','Understand the question','Recognize the farming topic across Telugu, English and mixed queries.'],['02','Extract useful details','Identify crop, symptoms, district and growth stage when the wording supplies them.'],['03','Provide a next step','Show sourced first actions, conditional calculations or the relevant official service.'],['04','Ask for missing details','Keep the original question attached when the farmer adds information.']];
 rows.forEach((r,i)=>{const y=158+i*110;txt(s,r[0],70,y,80,45,34,C.gold,true);txt(s,r[1],172,y,1000,42,29,C.green,true);txt(s,r[2],172,y+44,1010,58,26);});
}
// 4. Dataset.
{
 const s=slide('Dataset and label design',`The supplied workbook contains 12,625 rows and 20 original intent labels, with Telugu, English and code-mixed query columns. The pipeline maps the labels to seven farm topics and adds an authored out_of_scope class. Query versions and wording groups stay together during splitting. The split counts refer to expanded text examples, not the original workbook rows. The training count of 36,443 includes 16,206 synthetic examples. Out_of_scope has no genuine workbook test rows. Provenance does not establish real farmer authorship. Sources: ${source('reports/dataset_statistics.json')}; ${source('ml/models/metrics.json')}; ${source('ml/data.py')}; ${source('reports/dataset_audit.md')}.`);
 txt(s,'12,625 workbook rows',70,150,660,66,46,C.green,true);
 txt(s,'20 original intent labels',70,222,660,58,32,C.ink);
 txt(s,'Telugu, English and code-mixed query columns',70,295,650,98,30);
 txt(s,'Seven farm topics + authored out_of_scope',70,423,650,96,32,C.gold,true);
 txt(s,'Expanded text examples',805,150,390,50,29,C.green,true);
 txt(s,`Training  ${m.split_counts.train.toLocaleString('en-IN')}\nValidation  ${m.split_counts.validation.toLocaleString('en-IN')}\nTest  ${m.split_counts.test.toLocaleString('en-IN')}`,805,222,390,170,32);
 txt(s,`${m.split_counts.synthetic_training.toLocaleString('en-IN')} synthetic examples\nwithin training`,805,440,390,110,27);
 footer(s,'Dataset provenance and templates limit claims about real farmer use');
}
// 5. Methodology as flat editable stages, no fabricated illustration.
{
 const s=slide('Methodology',`Walk through the pipeline in order. NFC and Unicode L/M filtering retain Telugu letters and combining marks. Normalization removes punctuation, digits and URLs from classifier text and standardizes selected romanized spellings. It keeps stopwords. The implementation separately extracts quantities from the original query for calculations. TF-IDF word features use unigrams and bigrams; character features use char_wb n-grams of length 2 to 5. Classification predicts a topic, and entity/routing rules then guide the answer. Sources: ${source('ml/preprocess.py')}; ${source('ml/train.py')}; ${source('ml/slots.py')}; ${source('js/requests.js')}.`);
 const entries=[['1  Prepare text','Unicode normalization and selected spelling variants'],['2  Represent text','Word TF-IDF, character TF-IDF or their combination'],['3  Predict a topic','Naive Bayes, Logistic Regression or Linear SVM'],['4  Add context','Crop, symptom, location and focused question rules'],['5  Respond','Reviewed guidance, live lookup or a specific follow-up']];
 entries.forEach((r,i)=>{const y=150+i*89;txt(s,r[0],70,y,360,50,29,C.green,true);txt(s,r[1],465,y,730,65,28);});
}
// 6. Model selection protocol.
{
 const s=slide('Experiments and model selection',`Explain why nine experiments exist: three classifiers times three feature families. Group-aware five-fold CV uses original training text with fold-local TF-IDF. Synthetic coverage enters final model fitting, so CV and validation use different training regimes. Validation macro-F1 selects the winner, with accuracy as a tie-break. The saved selection is Logistic Regression with word features. The 319-query challenge is for reporting and must not retrospectively choose a different model. The character and combined models improve challenge scores, which provides a future research direction. Source: ${source('ml/train.py')}; ${source('reports/model_comparison.md')}.`);
 para(s,'Three classifiers','Multinomial Naive Bayes\nLogistic Regression\nLinear SVM',70,155,520);
 para(s,'Three feature sets','Word unigrams and bigrams\nCharacter n-grams, lengths 2–5\nCombined word + character features',690,155,520);
 txt(s,'Five-fold grouped cross-validation',70,415,1100,58,33,C.gold,true);
 txt(s,'Validation macro-F1 selects Logistic Regression with word TF-IDF',70,491,1110,90,35,C.green,true);
 footer(s,'The authored benchmark reports generalization after model selection');
}
// 7. Required editable evidence: all nine authored experiments.
{
 const s=slide('Results on the 319-query authored benchmark',`Every value comes from robustness.raw_models in the saved metrics. Raw selected Logistic Regression/word accuracy is ${pct(m.robustness.selected_raw.accuracy)} and macro-F1 is ${pct(m.robustness.selected_raw.macro_f1)}. Character and combined Logistic Regression both reach 88.09% accuracy on this challenge. The selected model remains fixed by validation selection. Macro-F1 is the unweighted mean of per-class F1. This authored challenge does not represent a farmer population survey. Chart values round to two displayed percentage decimals. Full-precision source records follow in these speaker notes. Source: ${source('ml/models/metrics.json')}, robustness.raw_models. Full-precision records: `+JSON.stringify(m.robustness.raw_models));
 const scores=m.comparison.map(r=>m.robustness.raw_models.find(x=>x.experiment===r.key));
 const chart=s.charts.add('bar',{position:{left:65,top:135,width:1145,height:470},categories:m.comparison.map(r=>r.model+' / '+r.features),series:[{name:'Accuracy',values:scores.map(r=>Number(r.accuracy.toFixed(4))),fill:C.green},{name:'Macro-F1',values:scores.map(r=>Number(r.macro_f1.toFixed(4))),fill:C.gold}],barOptions:{direction:'bar',grouping:'clustered',gapWidth:62},hasLegend:true,legend:{position:'top',textStyle:{typeface:'Arial',fontSize:22,fill:C.ink}},xAxis:{textStyle:{typeface:'Arial',fontSize:20,fill:C.ink}},yAxis:{tickLabelPosition:'none',min:0,max:1,numberFormatCode:'0%',majorUnit:.2,textStyle:{typeface:'Arial',fontSize:18,fill:C.muted},majorGridlines:{fill:C.line,width:1}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.00%',textStyle:{typeface:'Arial',fontSize:17,fill:C.ink}},chartFill:C.pale,plotAreaFill:C.pale});applyPresentationChartFont(chart,{fontFamily:'Arial'});
 footer(s,'Raw selected model: 79.00% accuracy and 80.02% macro-F1. All bars use a 0–100% scale.');
}
// 8. Native table, distinct evaluation protocols.
{
 const s=slide('Generalization depends on the evaluation set',`Read the first three rows as evaluations of the selected word-feature model. The workbook held-out set has 3,850 examples and seven genuine workbook classes. The original authored benchmark has 150 queries and the larger challenge has 319. The fourth row applies the saved deployed guard and slot rules to the same 319 queries. The fifth row uses a separately fitted combined-feature Logistic Regression with C=2 and a different transfer-training protocol, so it is not the selected word model's cross-script score. All rows are stored evaluation snapshots and predate the latest advisory/question-rule expansion. Source: ${source('ml/models/metrics.json')}; ${source('ml/robustness.py')}.`);
 const R=m.robustness;
 table(s,['Evaluation','Queries','Accuracy','Macro-F1'],[
 ['Selected model: workbook','3,850',pct(m.selected.test_accuracy),pct(m.selected.test_macro_f1)],
 ['Selected model: original authored','150',pct(m.handwritten.accuracy),pct(m.handwritten.macro_f1)],
 ['Selected model: larger authored','319',pct(R.selected_raw.accuracy),pct(R.selected_raw.macro_f1)],
 ['Saved routing rules + selected ML','319',pct(R.deployed_rules.accuracy),pct(R.deployed_rules.macro_f1)],
 ['Cross-script: separate combined LR','1,256',pct(R.cross_script.accuracy),pct(R.cross_script.macro_f1)]
 ],[570,150,210,210],{y:155,h:350,size:25});
 txt(s,'Different sizes and difficulty prevent a direct ranking of these sets',70,535,1120,50,27,C.gold,true);
 footer(s,'Cross-script uses a different model/training protocol. Saved rules differ from the latest expansion.');
}
// 9. Implementation.
{
 const s=slide('Implementation',`The site uses HTML, CSS and vanilla JavaScript. app.py serves Flask prediction and price endpoints. The exported winning estimator supports browser inference as a fallback, rather than a different centroid substitute. Shared slot configuration drives Python and browser rules. The answer layer uses curated text and service adapters; there is no generative LLM answering arbitrary questions. The optional Windows price adapter uses the working PowerShell connection path. API credentials stay server-side and no key appears in this presentation. Sources: ${source('app.py')}; ${source('js/classifier.js')}; ${source('js/entities.js')}; ${source('js/answers.js')}; ${source('js/requests.js')}; ${source('ml/prices.py')}.`);
 para(s,'Browser interface','HTML, CSS and vanilla JavaScript\nLanguage toggle and contextual follow-ups\nExported model for browser inference',70,155,540);
 para(s,'Local Python server','Flask /predict and /prices endpoints\nSaved scikit-learn estimator\nServer-side price-service connection',695,155,510);
 txt(s,'Shared configuration keeps Python and browser extraction aligned',70,430,1110,100,34,C.green,true);
 txt(s,'The answer layer combines reviewed guidance with service responses',70,548,1110,57,28,C.gold);
}
// 10. Real rendered crop answer evidence.
{
 const s=slide('Practical guidance from a recognized symptom',`Demonstrate the exact query: na potato chetu ki holes unnay em cheyali. The real website recognizes potato and the holes symptom. It gives leaf-surface inspection, cautious physical collection of identified caterpillars on a few plants and monitoring, then offers affected-part follow-ups. It does not establish a diagnosis from the word holes. Clicking tubers changes the checks to tunnels near the eyes and separate storage handling, using TNAU guidance. The screenshot excerpts the actual website action list with enlarged presentation typography, with no mocked API result. Sources: ${source('js/practical.js')}; ${source('tests/practical.cjs')}; https://ipm.ucanr.edu/home-and-landscape/leaf-feeding-caterpillars/ ; https://agritech.tnau.ac.in/crop_protection/potato/potato_2.html .`);
 txt(s,'“na potato chetu ki holes unnay em cheyali”',70,150,1135,70,36,C.gold,true);
 txt(s,'Crop: Potato     Symptom: Holes     Follow-up: Leaves, stems or tubers?',70,236,1135,65,28,C.green,true);
 await image(s,'steps.png',70,320,1140,255);
 footer(s,'Website action-list excerpt, enlarged for readability. These steps do not confirm the pest.');
}
// 11. Multilingual examples with actual source screenshot.
{
 const s=slide('Telugu, English and mixed-language questions',`These are authored functional regression examples, not a representative accuracy sample. Thirty variants cover the user's ten question types in Telugu, English and mixed forms. The shared configuration adds the Telugu chilli name and Telugu district aliases and recognizes soil testing, PM-KISAN, Rythu Bharosa and equipment rental requests. The slide uses editable text for actual Telugu and mixed regression examples plus an illustrative English weather question that contains an explicit place and date. Sources: ${source('tests/question_cases.json')}; ${source('tests/questions.cjs')}; ${source('data/slots.json')}; ${source('js/requests.js')}.`);
 txt(s,'Telugu',70,162,180,55,28,C.green,true);
 txt(s,'“ఈరోజు వరంగల్ మార్కెట్‌లో మిర్చి ధర ఎంత?”',280,154,925,90,32,C.green,true,'Nirmala UI');
 txt(s,'Chilli + Warangal + market price',280,251,925,45,26);
 txt(s,'English',70,330,180,55,28,C.green,true);
 txt(s,'“Will it rain in Warangal tomorrow?”',280,326,925,65,32,C.ink);
 txt(s,'Weather + district + requested date',280,397,925,45,26);
 txt(s,'Mixed',70,485,180,55,28,C.gold,true);
 txt(s,'“Hanamkonda దగ్గర soil testing ఎక్కడ చేస్తారు?”',280,477,925,90,31,C.gold,true,'Nirmala UI');
 txt(s,'Soil Health Card + Hanumakonda',280,565,925,45,26);
 footer(s,'The user can switch the interface language without changing the query');
}
// 12. Real service distinction.
{
 const s=slide('Weather, mandi prices and official services',`Weather uses Open-Meteo geocoding and the requested dated daily forecasts. Tomorrow uses the next day, and a three-day request uses three explicit dates including today. Missing location triggers a district selector. Mandi lookup uses the configured data.gov.in adapter and preserves commodity, market, reporting date and INR/quintal; older reports never become today's price. Unspecified chilli prompts dry/green clarification. Hanumakonda soil testing, PM-KISAN status, Rythu Bharosa forms and FARMS hiring use official public guidance and links. The assistant cannot inspect private payment status or confirm live equipment availability. External-service verification in regression tests uses explicit fixtures, not claims of observed current prices or weather. Sources: ${source('js/requests.js')}; ${source('ml/prices.py')}; https://open-meteo.com/en/docs ; https://www.pmkisan.gov.in/BeneficiaryStatus_New.aspx ; https://hanumakonda.telangana.gov.in/agriculture/ ; https://agrimachinery.nic.in/Index/farmsapp ; https://rythubharosa.telangana.gov.in/ .`);
 para(s,'Weather and prices','Dated forecasts for the selected location\nReported mandi rows with market and grade\nClear messages when services fail',70,155,535);
 para(s,'Official service routes','Soil Health Card and local lab information\nPM-KISAN status and Rythu Bharosa forms\nFARMS equipment-hiring directory',695,155,510);
 txt(s,'Missing information leads to a focused follow-up',70,440,1120,65,36,C.green,true);
 txt(s,'No invented weather, mandi prices, private status or rental availability',70,535,1120,70,29,C.gold);
}
// 13. Demo plus all-member participation without invented team identities.
{
 const s=slide('Live demonstration and team participation',`Suggested speaking allocation, not a claim about historical contributions: divide opening/data, NLP/modeling, implementation/demo, and results/conclusion among the actual team members. If the team size differs, split or combine these areas so everyone speaks. Demo in the local site: (1) enter the original potato holes query, (2) choose tubers and explain the contextual change, (3) ask the Telugu chilli/Warangal price query and choose dry/green, (4) ask about tomorrow's weather and select the district. Keep scheme and equipment examples as backup. Start the local server in advance. Internet is needed for weather and mandi services; if unavailable, show the honest service message and continue the crop-guidance demo. Sources: ${source('tests/question_cases.json')}; ${source('index.html')}.`);
 txt(s,'Suggested speaking areas',70,150,560,50,30,C.green,true);
 const roles=['Opening and dataset','NLP methodology and models','Implementation and demonstration','Results, limitations and conclusion'];roles.forEach((r,i)=>txt(s,`${i+1}  ${r}`,70,228+i*79,550,68,27));
 txt(s,'Demonstration sequence',705,150,500,50,30,C.gold,true);
 txt(s,'Potato holes question\nAffected-part follow-up\nTelugu chilli price question\nTomorrow’s local forecast',705,228,500,300,30);
 footer(s,'Every team member should explain a section and participate in questions');
}
// 14. Conclusion.
{
 const s=slide('Conclusion and future work',`Conclude that the project demonstrates a working classical NLP assistant for Telugu-English agricultural queries. The selected model's stored 319-query raw accuracy is 79.00%, and its macro-F1 is 80.02%. Saved routing rules improve that challenge accuracy to 83.39%, but the latest question-handling expansion has not been included in that stored metric. Cross-script transfer remains weak in macro-F1 and uses a separate combined-feature model. Workbook provenance and template effects limit external validity. Future work should collect consented real farmer questions, expand expert-reviewed local advice and validate transfer across scripts. Do not claim the system diagnoses diseases or answers every possible question. Sources: ${source('ml/models/metrics.json')}; ${source('reports/robustness.md')}; ${source('js/practical.js')}.`);
 para(s,'What the project demonstrates','A working NLP classifier connected to a multilingual website and practical farming workflows.',70,155,535);
 para(s,'What needs more evidence','Real farmer data, broader expert-reviewed advice and stronger cross-script generalization.',695,155,510);
 txt(s,'79.00% raw accuracy on the 319-query challenge',70,430,1120,70,38,C.green,true);
 txt(s,'Future work: field validation and stronger language-transfer models',70,542,1120,70,30,C.gold);
}
// 15. Appendix: exact displayed experiment values, native editable table.
{
 const s=slide('Appendix: complete experiment results',`Percentages display two decimal places. The native table provides all nine model/feature experiments. Workbook test metrics and larger authored challenge metrics come from the same saved metrics file, but reflect different evaluation sets. Source: ${source('ml/models/metrics.json')}, comparison and robustness.raw_models. Full-precision records: `+JSON.stringify(m.robustness.raw_models.map(r=>({experiment:r.experiment,accuracy:r.accuracy,macro_f1:r.macro_f1}))));
 const rows=m.comparison.map(r=>{const a=m.robustness.raw_models.find(x=>x.experiment===r.key);return [r.model,r.features,pct(a.accuracy),pct(a.macro_f1),pct(r.test_accuracy),pct(r.test_macro_f1)];});
 table(s,['Model','Features','Authored\naccuracy','Authored\nmacro-F1','Workbook\naccuracy','Workbook\nmacro-F1'],rows,[285,145,175,175,180,180],{y:153,h:450,size:23});
 footer(s,'Authored: 319 queries. Workbook test: 3,850 expanded text examples. Percentages rounded to two decimals.');
}
// 16. Appendix: functional verification and viva preparation.
{
 const s=slide('Appendix: verification and viva preparation',`The current reports record ${reports['test_summary.json'].passed} pytest checks, ${reports['questions_test_results.json'].passed} question-flow browser checks, ${reports['practical_test_results.json'].passed} practical-guidance browser checks and ${reports['charts_test_results.json'].passed} remaining chart/browser checks. The browser sum is ${browserPass}; these are functional checks with explicit external-service fixtures, not a field accuracy measure. For viva: TF-IDF measures term importance; word/character features address different spelling variation. Macro-F1 averages class-wise F1 equally. Validation selected the model; the authored challenge was not used to pick it. ML predicts intent while rules/entities supply context and the knowledge layer supplies reviewed advice. Sources: ${source('reports/test_summary.json')}; ${source('reports/questions_test_results.json')}; ${source('reports/practical_test_results.json')}; ${source('reports/charts_test_results.json')}; ${source('ml/train.py')}.`);
 txt(s,`${reports['test_summary.json'].passed} pytest checks`,70,158,570,65,42,C.green,true);
 txt(s,`${browserPass} browser checks`,70,240,570,65,42,C.gold,true);
 txt(s,'30 authored language variants\nZero reported JavaScript errors',70,350,570,115,29);
 txt(s,'Viva topics',745,158,460,50,30,C.green,true);
 txt(s,'Why TF-IDF?\nWhy macro-F1?\nWhy grouped splits?\nML versus routing rules\nWhy ask for clarification?',745,232,460,320,29);
 footer(s,'Functional checks use explicit API fixtures. Field performance requires separate validation.');
}

await fs.mkdir(path.join(build,'previews'),{recursive:true});
for(let i=0;i<all.length;i++){
 const b=await p.export({slide:all[i],format:'png',scale:1});
 await fs.writeFile(path.join(build,'previews',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));
}
await fs.writeFile(path.join(build,'deck.proto.json'),JSON.stringify(p.toProto()));
const candidate=path.join(build,'candidate_v3.pptx');await (await PresentationFile.exportPptx(p)).save(candidate);
const final=path.join(root,'presentations','Rythu_Mitra_NLP_Project_Presentation.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,pythonExecutable:path.join(runtime,'python','python.exe'),integrityValidatorPath:path.join(skill,'container_tools','inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools','inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','8','--require-native-table-slide','15'],explicitTotalSlideCount:16,requiredNativeTableOwnerSlides:[8,15],requiredNativeChartOwnerSlides:[7],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:['Arial','Nirmala UI']},verifyArtifactToolImport:true,receiptPath:path.join(build,'presentation.validation.json')});
console.log(JSON.stringify({final,slides:all.length,result}));
