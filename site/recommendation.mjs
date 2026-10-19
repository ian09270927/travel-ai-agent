export const AUDIENCES={family:'親子',couple:'情侶',senior:'熟齡'};
export const STYLES={nature:'自然生態',culture:'文化藝文',scenic:'景觀慢遊',music:'音樂活動'};
export const NOTICE='教學示範：行程、價格與天數為模擬，非旅行社報價。實際活動、費用、開放與交通須另行確認。';
export const money=n=>new Intl.NumberFormat('zh-TW').format(n);
export function todayTaipei(now=new Date()) {return new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Taipei',year:'numeric',month:'2-digit',day:'2-digit'}).format(now);}
export function parseDate(value){
 if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return null;
 const date=new Date(value+'T00:00:00Z');return Number.isFinite(date.getTime())&&date.toISOString().slice(0,10)===value?date:null;
}
export function validatePreferences(p,today=todayTaipei()){
 const errors={};
 if(!Object.hasOwn(AUDIENCES,p.audience))errors.audience='請選擇同行旅伴。';
 if(!['limited','undecided'].includes(p.budget_mode))errors.budget='請選擇預算方式。';
 if(p.budget_mode==='limited'&&(!Number.isSafeInteger(p.budget_per_person_twd)||p.budget_per_person_twd<=0))errors.budget='請輸入大於 0 的整數金額，單位為每人整趟新台幣。';
 if(![1,2,3].includes(p.days))errors.days='請選擇 1、2 或 3 天。';
 if(!Array.isArray(p.styles)||p.styles.length<1||p.styles.length>2||new Set(p.styles).size!==p.styles.length||p.styles.some(s=>!Object.hasOwn(STYLES,s)))errors.styles='請選擇 1–2 種旅行風格。';
 if(p.departure_date&&(!parseDate(p.departure_date)||p.departure_date<today))errors.date='請選擇有效且不早於今天的出發日期。';
 if(typeof p.notes!=='string'||[...p.notes].length>300)errors.notes='需求備註最多 300 字。';
 return errors;
}
export function prepareData(dataset,research){
 if(!dataset||dataset.data_mode!=='mock'||!Array.isArray(dataset.plans)||!research||!Array.isArray(research.records))throw Error('旅遊資料格式不正確。');
 const refs=new Map(research.records.map(r=>[r.id,r]));
 const counts=new Map();dataset.plans.forEach(p=>counts.set(p?.id,(counts.get(p?.id)||0)+1));
 const issues=[];
 const strings=a=>Array.isArray(a)&&a.length>0&&a.every(x=>typeof x==='string'&&x.trim());
 const valid=dataset.plans.filter(p=>{
  const ok=p&&/^MOCK-[\w-]+$/.test(p.id)&&counts.get(p.id)===1&&p.is_mock===true&&typeof p.title==='string'&&p.title.trim()&&typeof p.region==='string'&&p.region.trim()
   &&[1,2,3].includes(p.days)&&Number.isSafeInteger(p.demo_price_per_person_twd)&&p.demo_price_per_person_twd>0
   &&strings(p.audiences)&&p.audiences.every(a=>Object.hasOwn(AUDIENCES,a))&&strings(p.styles)&&p.styles.every(s=>Object.hasOwn(STYLES,s))
   &&strings(p.highlights)&&strings(p.cautions)&&strings(p.itinerary_outline)&&p.itinerary_outline.length===p.days
   &&strings(p.research_ids)&&p.research_ids.every(id=>{const r=refs.get(id);return r&&typeof r.name==='string'&&r.source&&/^https:\/\//.test(r.source.url)&&typeof r.queried_on==='string';})
   &&Array.isArray(p.event_requirements)&&p.event_requirements.every(e=>p.research_ids.includes(e.research_id)&&Number.isInteger(e.day_index)&&e.day_index>=1&&e.day_index<=p.days&&refs.get(e.research_id)?.type==='活動')
   &&p.research_ids.filter(id=>refs.get(id)?.type==='活動').every(id=>p.event_requirements.some(e=>e.research_id===id))
   &&strings(p.mock_fields)&&['title','days','demo_price_per_person_twd','itinerary_outline'].every(k=>p.mock_fields.includes(k))&&typeof p.mock_notice==='string'&&p.mock_notice.trim();
  if(!ok)issues.push({id:p?.id??'unknown',message:'必要欄位、模擬標示、來源或 ID 有誤，已排除。'});return !!ok;
 });
 return {plans:valid,refs,issues};
}
export function eventEligible(plan,p,refs,today){
 return plan.event_requirements.every(req=>{
  const dates=refs.get(req.research_id)?.activity_dates;
  if(!dates||!parseDate(dates.start)||!parseDate(dates.end)||dates.start>dates.end||dates.end<today||!p.departure_date)return false;
  const departure=parseDate(p.departure_date);if(!departure)return false;
  departure.setUTCDate(departure.getUTCDate()+req.day_index-1);const target=departure.toISOString().slice(0,10);
  return target>=dates.start&&target<=dates.end;
 });
}
export function recommend(data,p,today=todayTaipei()){
 const errors=validatePreferences(p,today);if(Object.keys(errors).length)return {errors,results:[]};
 const results=data.plans.filter(plan=>plan.audiences.includes(p.audience)&&plan.days===p.days
  &&(p.budget_mode==='undecided'||plan.demo_price_per_person_twd<=p.budget_per_person_twd)
  &&plan.styles.some(s=>p.styles.includes(s))&&eventEligible(plan,p,data.refs,today))
 .map(plan=>({plan,matchedStyles:plan.styles.filter(s=>p.styles.includes(s))}))
 .sort((a,b)=>b.matchedStyles.length-a.matchedStyles.length||a.plan.demo_price_per_person_twd-b.plan.demo_price_per_person_twd||a.plan.id.localeCompare(b.plan.id)).slice(0,3);
 return {errors:{},results};
}
export function reasonFor(result,p){return `符合${AUDIENCES[p.audience]}旅伴、${p.days} 天與${result.matchedStyles.map(s=>STYLES[s]).join('、')}偏好。`+(p.budget_mode==='limited'?`示範每人總價不超過你設定的 NT$ ${money(p.budget_per_person_twd)}。`:'預算尚未決定，本次未按金額篩選。');}
export function toggleBounded(ids,id,max=3){if(ids.includes(id))return {ids:ids.filter(x=>x!==id),limit:false};if(ids.length>=max)return {ids:[...ids],limit:true};return {ids:[...ids,id],limit:false};}
export function makeInquiry(results,p,refs){
 const lines=['台灣旅行｜諮詢需求單','資料模式：mock（本地教學示範）',NOTICE,'狀態：需求單已產生，尚未傳送給旅行社。','',`旅伴：${AUDIENCES[p.audience]}`,`天數：${p.days} 天`,`預算：${p.budget_mode==='limited'?'每人整趟上限 NT$ '+money(p.budget_per_person_twd):'尚未決定'}`,`旅行風格：${p.styles.map(s=>STYLES[s]).join('、')}`,`出發日期：${p.departure_date||'尚未選擇'}`,`備註：${p.notes.trim()||'無'}`,''];
 results.forEach((r,i)=>{const plan=r.plan;lines.push(`${i+1}. ${plan.title}（${plan.id}）`,`${plan.region}／${plan.days} 天／每人示範總價 NT$ ${money(plan.demo_price_per_person_twd)}`,`推薦原因：${reasonFor(r,p)}`,'每日提綱（模擬）：'+plan.itinerary_outline.map((t,j)=>`第 ${j+1} 天 ${t}`).join('；'),'待確認：'+plan.cautions.join(' '));
  plan.research_ids.forEach(id=>{const ref=refs.get(id);lines.push(`官方景點／活動資訊：${ref.name}，查詢日 ${ref.queried_on}，${ref.source.url}`)});
  plan.event_requirements.forEach(e=>{const d=refs.get(e.research_id).activity_dates;lines.push(`活動公告期間：${d.start}～${d.end}；日期落在公告期間，實際場次待確認。`)});lines.push('');
 });
 lines.push('請另行確認實際行程、報價、開放、交通及移動條件。本網站未收件或預訂。');return lines.join('\n');
}
