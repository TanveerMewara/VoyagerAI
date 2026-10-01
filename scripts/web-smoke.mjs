import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || path.join(process.cwd(), "package.json"));
const { chromium } = require("playwright-core");
const origin = process.env.TEST_ORIGIN || "http://127.0.0.1:8502";
const report = "# Itinerary\nDay 1: Louvre and a park.\n---\n# Budget Breakdown\n| Category | Cost (EUR) |\n|---|---|\n| Hotel | 400 |\n| Food | 200 |\n| Total | 600 |\n---\n# Hotel Recommendations\nThree estimated options.\n---\n# Travel Tips\nVerify opening times.\n---\n# Weather\nCurrent conditions only.";
const browser = await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE || "C:/Program Files/Google/Chrome/Application/chrome.exe",headless:true});
fs.mkdirSync("data/evaluation/web",{recursive:true});
try {
 for (const size of [{width:1440,height:1000},{width:390,height:844}]) {
  const page=await browser.newPage({viewport:size});
  const errors=[];
  page.on("pageerror",error=>errors.push(error.message));
  await page.route("**/api/plan",route=>route.fulfill({status:200,contentType:"application/x-ndjson",body:JSON.stringify({type:"text",text:"# Itinerary\nDay 1"})+"\n"+JSON.stringify({type:"done",text:report,generation_seconds:4,first_text_seconds:1.5})+"\n"}));
  await page.route("**/api/chat",route=>route.fulfill({status:200,contentType:"application/x-ndjson",body:JSON.stringify({type:"done",text:"Use the metro.",generation_seconds:1,first_text_seconds:.5})+"\n"}));
  await page.goto(origin,{waitUntil:"networkidle"});
  await page.locator('input[name="destination"]').fill("Paris");
  await page.locator('input[name="budget"]').fill("EUR 1500");
  await page.locator("#generate").click();
  await page.locator("#status").filter({hasText:"Plan ready"}).waitFor();
  assert.equal(await page.locator("#download").isEnabled(),true);
  await page.locator('[data-tab="analytics"]').click();
  await page.waitForTimeout(500);
  assert.equal(await page.locator("#budget-table tr").count(),2);
  await page.locator('[data-tab="map"]').click();
  await page.locator(".leaflet-marker-icon").waitFor();
  await page.waitForTimeout(1500);
  await page.screenshot({path:"data/evaluation/web/map-"+size.width+".png",fullPage:true});
  const loadedTiles=await page.locator(".leaflet-tile-loaded").count();
  assert.ok(loadedTiles>0,"Map tiles render");
  await page.locator('[data-tab="chat"]').click();
  await page.locator("#question").fill("Transport?");
  await page.locator("#send").click();
  await page.locator(".message.assistant").filter({hasText:"Use the metro."}).waitFor();
  await page.route("**/api/plan",route=>route.fulfill({status:200,contentType:"application/x-ndjson",body:JSON.stringify({type:"error",message:"Gemini is temporarily busy"})+"\n"}));
  await page.locator("#generate").click();
  await page.locator("#error").waitFor();
  assert.match(await page.locator("#report-content").textContent(),/Louvre/);
  assert.equal(await page.locator("#download").isEnabled(),true);
  assert.equal(await page.locator("#question").isEnabled(),true);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,"No horizontal overflow");
  await page.screenshot({path:"data/evaluation/web/workspace-"+size.width+".png",fullPage:true});
  assert.deepEqual(errors,[]);
  console.log("PASS: desktop/mobile tabs, chart, loaded map tiles, chat, failure preservation and no page errors at "+size.width);
  await page.close();
 }
} finally { await browser.close(); }
