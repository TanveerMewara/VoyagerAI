const $ = (selector) => document.querySelector(selector);
let savedPlan = "", chart = null, map = null, marker = null, busy = false;
const render = (text) => DOMPurify.sanitize(marked.parse(text));
function activate(name) {
  document.querySelectorAll(".view").forEach(v => v.classList.toggle("active", v.id === name));
  document.querySelectorAll("[data-tab]").forEach(b => b.classList.toggle("active", b.dataset.tab === name));
  if (name === "map" && map) setTimeout(() => map.invalidateSize(), 50);
}
document.querySelectorAll("[data-tab]").forEach(button => button.addEventListener("click", () => activate(button.dataset.tab)));
function showError(message) { $("#error").textContent = message; $("#error").hidden = false; }
async function stream(url, data, update) {
  const response = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(data)});
  if (!response.ok) throw new Error(response.status === 422 ? "Please check your trip details." : "Request failed. Please try again.");
  const reader = response.body.getReader(), decoder = new TextDecoder();
  let buffer = "", done = null;
  function consume(line) {
    if (!line.trim()) return;
    const item = JSON.parse(line);
    if (item.type === "error") throw new Error(item.message);
    if (item.type === "text") update(item.text);
    if (item.type === "done") { done = item; update(item.text); }
  }
  try {
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      buffer += decoder.decode(chunk.value, {stream:true});
      const lines = buffer.split("\n"); buffer = lines.pop();
      lines.forEach(consume);
    }
    buffer += decoder.decode();
    if (buffer.trim()) consume(buffer);
    if (!done) throw new Error("The response was interrupted. Please try again.");
    return done;
  } finally { await reader.cancel(); }
}
function budgetAnalytics(report) {
  const section = report.split(/^#\s+Budget Breakdown\s*$/mi)[1]?.split(/^#\s/m)[0] || "";
  const costs = [];
  section.split("\n").forEach(line => {
    const cells = line.split("|").map(cell => cell.replace(/\*\*/g,"").trim()).filter(Boolean);
    if (cells.length !== 2 || /total|category|---/i.test(cells[0])) return;
    const number = cells[1].replace(/[^\d.,-]/g,"").replace(/,/g,"");
    if (!/^\d+(\.\d+)?$/.test(number)) return;
    costs.push({label:cells[0],value:Number(number)});
  });
  if (chart) { chart.destroy(); chart = null; }
  $("#budget-table").replaceChildren();
  if (!costs.length) { $("#budget-note").textContent = "The expense breakdown is available in your plan; no comparable numeric table was returned."; return; }
  $("#budget-note").textContent = "Estimated allocations from your generated plan. Values use the currency shown in its budget table.";
  chart = new Chart($("#budget-chart"), {type:"doughnut",data:{labels:costs.map(c=>c.label),datasets:[{data:costs.map(c=>c.value),backgroundColor:["#087e79","#f0b54d","#487db1","#c97677","#79a984","#9a8bb1"],borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom"}}}});
  const table = document.createElement("table");
  costs.forEach(cost => { const row=table.insertRow(); row.insertCell().textContent=cost.label; row.insertCell().textContent=cost.value.toLocaleString(); });
  $("#budget-table").append(table);
}
async function destinationMap(destination) {
  if (marker && map) { map.removeLayer(marker); marker = null; }
  const response = await fetch("/api/location?destination="+encodeURIComponent(destination));
  if (!response.ok) throw new Error("Map unavailable");
  const data = await response.json();
  if (!data.coordinates) {
    $("#map-note").textContent = "No map coordinates are available for "+destination+".";
    if (map) map.setView([20,0],2);
    return;
  }
  if (!map) {
    map = L.map("destination-map").setView(data.coordinates,10);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);
  }
  map.setView(data.coordinates,10);
  const popup = document.createElement("span"); popup.textContent=destination;
  marker = L.marker(data.coordinates).addTo(map).bindPopup(popup);
  $("#map-note").textContent=destination;
}
$("#trip-form").addEventListener("submit", async event => {
  event.preventDefault(); if (busy) return;
  busy = true; $("#generate").disabled = true; $("#error").hidden = true;
  $("#status").textContent = "Preparing your plan and checking weather...";
  const data = Object.fromEntries(new FormData(event.target)); data.days=Number(data.days);
  activate("report"); $("#welcome").hidden=true; $("#report-content").hidden=false;
  try {
    const result = await stream("/api/plan",data,text => { $("#report-content").innerHTML=render(text); $("#status").textContent="Building your plan..."; });
    savedPlan=result.text; $("#chat-messages").replaceChildren(); $("#trip-summary").textContent=data.destination+" · "+data.days+" days · "+data.travelers;
    $("#timing").textContent="First text "+result.first_text_seconds+"s · Complete "+result.generation_seconds+"s";
    $("#download").disabled=false; $("#question").disabled=false; $("#send").disabled=false;
    $("#status").textContent="Plan ready";
    budgetAnalytics(savedPlan);
    destinationMap(data.destination).catch(()=>{$("#map-note").textContent="Map is temporarily unavailable.";});
  } catch(error) {
    showError(error.message); $("#status").textContent="";
    if(savedPlan) $("#report-content").innerHTML=render(savedPlan);
    else { $("#report-content").hidden=true; $("#welcome").hidden=false; }
  } finally { busy=false; $("#generate").disabled=false; }
});
$("#download").addEventListener("click",async()=>{
  $("#download").disabled=true; $("#error").hidden=true;
  try {
    const response=await fetch("/api/pdf",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({plan:savedPlan})});
    if(!response.ok) throw new Error("PDF could not be generated. Please try again.");
    const url=URL.createObjectURL(await response.blob()), link=document.createElement("a");
    link.href=url; link.download="VoyagerAI_TravelPlan.pdf"; link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
  } catch(error) {showError(error.message);} finally {$("#download").disabled=false;}
});
function message(role,text) {
  const box=document.createElement("div"); box.className="message "+role;
  const heading=document.createElement("strong"); heading.textContent=role==="user"?"You":"Voyager AI";
  const content=document.createElement("div"); content.innerHTML=render(text); box.append(heading,content); $("#chat-messages").append(box); return content;
}
$("#chat-form").addEventListener("submit",async event=>{
  event.preventDefault(); const question=$("#question").value.trim();
  if(!question||!savedPlan||busy) return;
  busy=true; $("#send").disabled=true; $("#generate").disabled=true; $("#error").hidden=true;
  message("user",question); $("#question").value=""; const content=message("assistant","...");
  try {await stream("/api/chat",{plan:savedPlan,question},text=>{content.innerHTML=render(text);content.scrollIntoView({block:"nearest"});});}
  catch(error){content.textContent=error.message;}
  finally{busy=false;$("#send").disabled=false;$("#generate").disabled=false;$("#question").focus();}
});
lucide.createIcons();
