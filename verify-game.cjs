const fs=require('fs'),vm=require('vm'),assert=require('assert');
class El{constructor(){this.children=[];this.style={};this.classList={add(){},remove(){},toggle(){}};this.open=false;this.disabled=false;this.textContent='';}append(e){this.children.push(e)}replaceChildren(...e){this.children=e}setAttribute(){}focus(){}scrollIntoView(){}remove(){}addEventListener(){}showModal(){this.open=true}close(){this.open=false}}
const els={},stored={},queue=[];const sandbox={console,document:{getElementById:id=>els[id]??=new El(),createElement:()=>new El(),addEventListener(){},querySelectorAll(){return []}},localStorage:{getItem:k=>stored[k]||null,setItem:(k,v)=>stored[k]=v},window:{scrollTo(){}},setTimeout:f=>{queue.push(f)},clearTimeout(){},setInterval(){return 1},clearInterval(){}};
vm.createContext(sandbox);const html=fs.readFileSync(process.argv[2]||'output/index.html','utf8');vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],sandbox);const run=code=>vm.runInContext(code,sandbox);function flush(){while(queue.length)queue.shift()()}
run('save.sound=false');assert.equal(els.chapters.children.filter(c=>!c.children.at(-1).disabled).length,3);

for(let c=0;c<3;c++){
 run(`start(${c})`);
 for(let i=0;i<10;i++){
  assert.equal(run('run.q'),i);
  run('answer(BANK[run.ch][run.q].answerIndex)');flush();
  const count=run('run.correct');run('answer(0)');assert.equal(run('run.correct'),count,'double answer blocked');
  if(i===2){assert.equal(run('run.energy'),100);run('ultimate()');flush();assert.equal(run('run.energy'),0);}
  if(run('run.enemy')>0){run('next()');flush();}
  run('next()');flush();
 }
 assert.equal(run(`save.best[${c}]`),10);assert.equal(els.modal.open,true);assert.equal(els.modalContent.innerHTML.includes('<h2>修仙成功'),c===2);els.modalActions.children[0].onclick();
}
assert(run('save.coins')>0);const old=run('hpMax()');run("upgrade('hp')");assert.equal(run('hpMax()'),old+30);
run('start(0)');const before=run('run.hp');run('answer((BANK[0][0].answerIndex+1)%4)');flush();assert.equal(run('run.hp'),before-25);assert.equal(run('run.combo'),0);assert(els.explanation.textContent.length>20);run('next()');flush();run('next()');assert.equal(run('run.q'),1);
for(let i=0;i<8&&!els.modal.open;i++){run('answer((BANK[run.ch][run.q].answerIndex+1)%4)');flush();if(!els.modal.open){run('next()');flush();run('next()')}}
assert.equal(run('run.missed.length'),3);assert(run('run.hp')>0);assert.equal(els.modal.open,true);assert(els.modalContent.innerHTML.includes('三命已盡'));
const reloaded={...sandbox,document:{...sandbox.document,getElementById:id=>new El()}};vm.createContext(reloaded);vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],reloaded);assert.equal(vm.runInContext('save.best.filter(x=>x===10).length',reloaded),3);
els.modal.close();run('start(1)');assert.equal(run('run.missed.length'),0);assert.equal(run('remaining()'),300);run('run.deadline=Date.now()-1;tick()');assert(els.modalContent.innerHTML.includes('時限已至'));const frozen=run('run.q');run('next();answer(0);ultimate()');assert.equal(run('run.q'),frozen);assert.equal(run('run.ended'),true);
assert(!/<(?:script|link)[^>]+(?:src|href)=["']https?:/i.test(html));
console.log('PASS: all 30 questions, 3 chapter clears, boss pursuit, ultimate, double-click guard, wrong-answer correction, defeat, upgrade, persisted reload, no external dependencies.');
