"use strict";
const $ = id => document.getElementById(id);
const symbols = {CLOSED:"✓",OPEN:"◇",FALSIFIED:"⊗",REMAP:"↪",PATCH:"+",FLIP:"⇄"};
let report, selected;
const text = (tag, value, cls) => {const el=document.createElement(tag);el.textContent=String(value);if(cls)el.className=cls;return el;};
const pretty = value => JSON.stringify(value,null,2);
function validate(value) {
  if(value?.format!=="upi-oden-knots" || value.version!=="1.0" || !Array.isArray(value.knots) || value.knots.length>10000 || !Array.isArray(value.paths)) throw Error("Expected an ODEN 1.0 result document.");
  for(const k of value.knots) {
    if(!Object.hasOwn(symbols,k.state) || !k.a?.observation || !k.b?.observation || !Array.isArray(k.red_tests) || !Array.isArray(k.causes) || !k.score_components || !Number.isFinite(k.score_components.score) || !Number.isFinite(k.confidence) || !k.tolerance) throw Error("Incomplete knot record.");
  }
  return value;
}
function load(value) {
  report=validate(value);selected=report.knots[0]?.id;
  $("filters").replaceChildren();
  for(const name of ["time","domain","type","state","confidence","source","score"]) {
    const label=text("label",name==="score"||name==="confidence"?`Minimum ${name}`:name);
    const input=document.createElement(name==="state"?"select":"input");input.id=`filter-${name}`;
    if(name==="state") for(const v of ["",...Object.keys(symbols)]) {const o=text("option",v||"All states");o.value=v;input.append(o);}
    else if(name==="score"||name==="confidence") {input.type="number";input.min="0";input.max="1";input.step="0.1";input.value="0";}
    else {input.type="search";input.placeholder="All";}
    input.addEventListener("input",render);label.append(input);$("filters").append(label);
  }
  render();
}
function filtered(k) {
  const a=k.a.observation,b=k.b.observation;
  const fields={time:`${a.time} ${b.time}`,domain:`${a.domain} ${b.domain}`,type:k.causes.join(" "),state:k.state,source:`${a.source} ${b.source}`};
  return Object.entries(fields).every(([key,value])=>String(value).toLowerCase().includes($("filter-"+key).value.toLowerCase())) && k.confidence>=Number($("filter-confidence").value) && k.score_components.score>=Number($("filter-score").value);
}
function render() {
  const knots=report.knots.filter(filtered).sort((a,b)=>b.score_components.score-a.score_components.score);
  if(!knots.some(k=>k.id===selected)) selected=knots[0]?.id;
  $("agrees").textContent=`${knots.filter(k=>k.state==="CLOSED").length} checkpoints close`;
  $("breaks").textContent=knots.find(k=>k.state!=="CLOSED")?.checkpoint||"No break in visible checkpoints";
  $("why").textContent=knots.some(k=>k.state==="OPEN")?"A cause still needs evidence":"Inspect the declared scope";
  $("map").replaceChildren();$("empty").hidden=knots.length>0;
  for(const k of knots) {
    const row=document.createElement("button");row.type="button";row.className="knot-row";row.dataset.state=k.state;row.setAttribute("aria-pressed",String(k.id===selected));row.setAttribute("aria-label",`${k.checkpoint}: ${k.state}`);
    row.append(text("span",k.a.observation.name,"node"));const knot=text("span",`${symbols[k.state]} ${k.state}`,"knot-symbol");knot.append(text("small",k.checkpoint));row.append(knot,text("span",k.b.observation.name,"node"));row.onclick=()=>{selected=k.id;render();};$("map").append(row);
  }
  detail(knots.find(k=>k.id===selected));
}
function detail(k) {
  const panel=$("detail");panel.replaceChildren();if(!k){panel.append(text("p","Choose a knot or adjust your filters."));return;}
  panel.append(text("p",`${k.id} · ${k.status}`,"eyebrow"),text("h3",k.checkpoint),text("p",`${symbols[k.state]} ${k.state} · score ${k.score_components.score.toFixed(3)}`,"badge"));
  panel.append(text("p",k.stop_reason||"Both representations agree within the declared tolerance."));
  const mirror=text("div","","mirror");
  for(const [label,value,cls] of [["PATH A",k.a.observation.raw_value,""],["ε",k.epsilon===null?"incompatible types":k.epsilon,"epsilon"],["PATH B",k.b.observation.raw_value,""]]){const col=text("div",value,cls);col.prepend(text("small",label));mirror.append(col);}panel.append(mirror);
  const dl=document.createElement("dl");
  const entries={Decision:k.decision,Units:k.units,Tolerance:pretty(k.tolerance),Uncertainty:pretty(k.uncertainty),"Source A":k.a.observation.source,"Source B":k.b.observation.source,Timestamps:`${k.a.observation.time} | ${k.b.observation.time}`,"Path A":k.path_a,"Path B":k.path_b,Mirror:`${k.a.mirror} | ${k.b.mirror}`,"First failure":k.first_failed_relation||"None","Failed bridge":pretty(k.first_failed_bridge),"Last safe node":k.last_safe_node||"No prior verified checkpoint",Explanations:k.causes.join(", ")||"Exact closure","Next observation":k.next_observation};
  for(const [key,value] of Object.entries(entries)) dl.append(text("dt",key),text("dd",value));panel.append(dl);
  const red=document.createElement("details");red.open=true;red.append(text("summary","RED / self-attack results"));const list=text("ul","","red-list");for(const r of k.red_tests){const li=text("li",`${r.result} · ${r.check} [${r.status}]`);li.append(text("small",r.evidence));list.append(li);}red.append(list);panel.append(red);
  for(const [label,value] of [["Score components",k.score_components],["Both paths / transformation history",report.paths.filter(p=>[k.path_a,k.path_b].includes(p.id))],["Raw observations / provenance",{a:k.a.observation,b:k.b.observation,controls:report.control_provenance}],["Preservation / decision history",{quarantined:k.quarantined,history:k.history,patch_not_erase:report.patch_not_erase}]]) {const d=document.createElement("details");d.append(text("summary",label),text("pre",pretty(value)));panel.append(d);}
}
$("filters").onsubmit=e=>e.preventDefault();
$("import").onchange=async e=>{try{const file=e.target.files[0];if(!file)return;if(file.size>5000000)throw Error("Result file exceeds 5 MB.");load(JSON.parse(await file.text()));$("message").textContent="Imported result · claims and provenance supplied by the file; not independently verified.";}catch(error){$("message").textContent=error.message;}};
$("export").onclick=()=>{if(!report)return;const url=URL.createObjectURL(new Blob([pretty(report)],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download="oden-knots.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
$("analyze").onclick=async()=>{try{const body=JSON.stringify(JSON.parse($("input").value));const response=await fetch("/api/knots/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body});if(!response.ok)throw Error("Analysis needs the local UPI Python server and a valid path document. Static hosts can open precomputed results.");load(await response.json());$("message").textContent="Analyzed supplied paths · software_test; no physical claim promoted.";}catch(error){$("message").textContent=error.message;}};
fetch("knots.json").then(r=>{if(!r.ok)throw Error("Could not load knot data.");return r.json();}).then(load).catch(e=>{$("message").textContent=e.message;});
