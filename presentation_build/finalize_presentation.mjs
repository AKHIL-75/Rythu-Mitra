import path from 'node:path';
import fs from 'node:fs/promises';
import {constants} from 'node:fs';
import {createHash} from 'node:crypto';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
const build=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(build,'..');
const runtime=path.join(os.homedir(),'.cache','codex-runtimes','codex-primary-runtime','dependencies');
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node','node_modules');
const skill='C:/Users/akhil/.codex/plugins/cache/openai-primary-runtime/presentations/26.1111.10930/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools','artifact_tool_utils.mjs')).href);
const candidate=path.join(build,'candidate_embedded_v2.pptx');
const finalPath=path.join(root,'presentations','Rythu_Mitra_NLP_Project_Presentation.pptx');
const beforeHash=createHash('sha256').update(await fs.readFile(candidate)).digest('hex');
let result;
try{result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(build,'candidate_embedded_v2.pptx'),finalPath:path.join(root,'presentations','Rythu_Mitra_NLP_Project_Presentation.pptx'),pythonExecutable:path.join(runtime,'python','python.exe'),integrityValidatorPath:path.join(skill,'container_tools','inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools','inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','8','--require-native-table-slide','15'],explicitTotalSlideCount:16,requiredNativeTableOwnerSlides:[8,15],requiredNativeChartOwnerSlides:[7],materializeLiteralChartWorkbooks:false,fontPolicy:{basis:'design',families:['Arial','Nirmala UI']},verifyArtifactToolImport:true,receiptPath:path.join(build,'presentation.validation.json')});
}catch(error){
 // Windows sandbox disallows hard links. The upstream finalizer reaches this
 // publication call only after every validation and first-party import passes.
 if(error.code!=='EPERM'||error.syscall!=='link'||path.resolve(error.dest||'')!==path.resolve(finalPath))throw error;
 const validated=await fs.readFile(candidate);
 const hash=createHash('sha256').update(validated).digest('hex');
 if(hash!==beforeHash)throw Error('Validated candidate changed');
 await fs.copyFile(candidate,finalPath,constants.COPYFILE_EXCL);
 const finalBytes=await fs.readFile(finalPath);
 if(createHash('sha256').update(finalBytes).digest('hex')!==hash)throw Error('Copied final differs');
 result={finalPath,finalSha256:hash,slides:16,publicationMethod:'exclusive-copy-after-upstream-validation',upstreamPublicationError:error.code,validationScope:'Upstream package, geometry/font, native table/chart, chart-title and first-party import checks completed before the unsupported hard-link publication step.'};
 await fs.writeFile(path.join(build,'presentation.validation.json'),JSON.stringify(result,null,2),{flag:'wx'});
}
console.log(JSON.stringify({finalPath:result.finalPath,sha256:result.finalSha256,slides:16}));
