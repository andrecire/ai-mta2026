(() => {
  'use strict';
  const D = window.WORKSHOP_DATA;
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => [...document.querySelectorAll(s)];
  const selected = new Map();
  function contentsMenu() {
    const trigger=document.createElement('button');
    trigger.id='deck-contents';trigger.type='button';trigger.textContent='Contents';
    trigger.setAttribute('aria-haspopup','dialog');trigger.setAttribute('aria-controls','contents-dialog');trigger.setAttribute('aria-expanded','false');
    const dialog=document.createElement('dialog');dialog.id='contents-dialog';dialog.setAttribute('aria-labelledby','contents-title');
    const header=document.createElement('header'),title=document.createElement('h2'),close=document.createElement('button');
    title.id='contents-title';title.textContent='Contents';
    close.type='button';close.className='contents-close';close.textContent='×';close.setAttribute('aria-label','Close contents');
    header.append(title,close);
    const nav=document.createElement('nav');nav.setAttribute('aria-label','Slides');
    const list=document.createElement('ol');
    $$('.slides > section').forEach((slide,index)=>{
      const item=document.createElement('li'),link=document.createElement('button');
      link.type='button';link.dataset.slide=index;link.textContent=slide.querySelector('h2').textContent;
      link.addEventListener('click',()=>{dialog.close();Reveal.slide(index,0,-1);trigger.blur();});
      item.append(link);list.append(item);
    });
    nav.append(list);dialog.append(header,nav);document.body.append(trigger,dialog);
    trigger.addEventListener('click',()=>{
      const current=Reveal.getIndices().h;
      dialog.querySelectorAll('[data-slide]').forEach(link=>{
        if(Number(link.dataset.slide)===current)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');
      });
      dialog.showModal();trigger.setAttribute('aria-expanded','true');
      dialog.querySelector('[aria-current="page"]').focus();
    });
    close.addEventListener('click',()=>dialog.close());
    dialog.addEventListener('close',()=>trigger.setAttribute('aria-expanded','false'));
    dialog.addEventListener('keydown',event=>event.stopPropagation());
    dialog.addEventListener('click',event=>{
      if(event.target!==dialog)return;
      const r=dialog.getBoundingClientRect();
      if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();
    });
  }
  function footer() {
    $$('.slides > section').forEach(section => {
      const f = document.createElement('footer'); f.className = 'deck-footer';
      const credit = document.createElement('p'); credit.className = 'credit'; credit.textContent = 'Andre A. Cire';
      const logo = document.createElement('img'); logo.src = $('#utsc-management-asset').src; logo.alt = 'University of Toronto Scarborough Management — Experience to Lead';
      f.append(credit,logo); section.append(f);
    });
  }
  function toolsMenu() {
    const toolbar=document.createElement('nav');toolbar.id='deck-toolbar';toolbar.setAttribute('aria-label','Presentation controls');
    const trigger=document.createElement('button');trigger.id='deck-tools';trigger.type='button';trigger.textContent='Tools';
    trigger.setAttribute('aria-haspopup','dialog');trigger.setAttribute('aria-controls','tools-dialog');trigger.setAttribute('aria-expanded','false');
    toolbar.append($('#deck-contents'),trigger);document.body.append(toolbar);
    const dialog=document.createElement('dialog');dialog.id='tools-dialog';dialog.setAttribute('aria-labelledby','tools-title');
    dialog.innerHTML='<header><h2 id="tools-title">Tools</h2><button type="button" class="tools-close" aria-label="Close tools">×</button></header><div class="tools-actions"><a id="tools-pdf" target="_blank" rel="noopener"><strong>Generate PDF</strong><span>Open printable slides, then Save as PDF.</span></a><button type="button" id="tools-fullscreen"><strong>Full screen</strong><span>Use the whole screen for presenting.</span></button><button type="button" id="tools-overview"><strong>Slide overview</strong><span>See all slides at once.</span></button><button type="button" id="tools-restart"><strong>Back to first slide</strong><span>Return to the workshop title.</span></button></div><p id="tools-status" role="status"></p>';
    document.body.append(dialog);
    const pdfURL=new URL(location.href);pdfURL.searchParams.set('print-pdf','');pdfURL.searchParams.set('export-pdf','1');pdfURL.hash='';
    $('#tools-pdf').href=pdfURL.href;
    function open(){dialog.showModal();trigger.setAttribute('aria-expanded','true');$('#tools-pdf').focus();}
    function close(){dialog.close();trigger.blur();}
    trigger.addEventListener('click',open);$('.tools-close').addEventListener('click',close);
    dialog.addEventListener('close',()=>trigger.setAttribute('aria-expanded','false'));
    dialog.addEventListener('keydown',event=>event.stopPropagation());
    dialog.addEventListener('click',event=>{if(event.target!==dialog)return;const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)close();});
    $('#tools-pdf').addEventListener('click',close);
    $('#tools-fullscreen').addEventListener('click',async()=>{
      close();
      try {if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}
      catch {$('#tools-status').textContent='Full screen is unavailable here. Try your browser’s full-screen control.';open();}
    });
    document.addEventListener('fullscreenchange',()=>{$('#tools-fullscreen strong').textContent=document.fullscreenElement?'Exit full screen':'Full screen';});
    $('#tools-overview').addEventListener('click',()=>{close();Reveal.toggleOverview();});
    $('#tools-restart').addEventListener('click',()=>{close();Reveal.toggleOverview(false);Reveal.slide(0,0,-1);});
  }
  function preparePrintView() {
    if(!Reveal.isPrintView())return;
    document.documentElement.classList.add('workshop-print');
    stopNetwork();tokenStep=1;renderTokens();
    $$('.slides .fragment').forEach(element=>element.classList.add('visible'));
    $$('.example-concealed').forEach(element=>{element.classList.remove('example-concealed');element.setAttribute('aria-hidden','false');element.inert=false;});
    $$('[data-reveal-target],#show-station-example').forEach(button=>button.hidden=true);
    $$('.comparison-table tbody tr').forEach(row=>row.setAttribute('aria-hidden','false'));
    $('#understand-data').dataset.readingStep='checks';
    $('#one-shot').dataset.step='0';$('.comparison-panel').setAttribute('aria-hidden','false');
    const controls=document.createElement('div');controls.id='pdf-controls';
    controls.innerHTML='<button type="button" id="pdf-save" disabled>Save as PDF</button><a id="pdf-return">Back to slides</a><span id="pdf-help" role="status">Preparing print layout…</span>';
    const slideURL=new URL(location.href);slideURL.searchParams.delete('print-pdf');slideURL.searchParams.delete('export-pdf');slideURL.hash='workshop-title';
    document.body.append(controls);$('#pdf-return').href=slideURL.href;$('#pdf-save').addEventListener('click',()=>window.print());
    let prepared=false;
    async function ready(){
      if(prepared)return;prepared=true;
      await document.fonts.ready;
      await Promise.all([...document.images].map(img=>img.decode().catch(()=>{})));
      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
      $('#pdf-save').disabled=false;$('#pdf-help').textContent='Choose “Save as PDF”. Enable background graphics; disable headers and footers.';
      window.PDF_READY=true;
      if(new URLSearchParams(location.search).get('export-pdf')==='1')window.print();
    }
    Reveal.on('pdf-ready',ready);
    if($('.pdf-page'))ready();
  }
  function allocation() {
    D.stations.forEach(station => {
      const tr = document.createElement('tr');
      const label = document.createElement('td'); label.textContent = station.station; tr.append(label);
      D.windows.forEach((window,index) => {
        const td = document.createElement('td'), button = document.createElement('button');
        button.type = 'button'; button.textContent = '○'; button.dataset.key = `${station.station_id}-${index}`;
        button.setAttribute('aria-label', `${station.station}, ${window}`);
        button.setAttribute('aria-pressed','false');
        button.addEventListener('click', () => {
          const key = button.dataset.key, passengers = station.expected_passengers[index];
          if (selected.has(key)) selected.delete(key);
          else if (selected.size === 3) return allocationStatus('Three pairs selected. Deselect one to try another.',true);
          else selected.set(key,passengers);
          allocationStatus();
        });
        td.append(button); tr.append(td);
      });
      $('#allocation-rows').append(tr);
    });
    $('#reset-allocation').addEventListener('click', () => { selected.clear(); allocationStatus(); });
  }
  function allocationStatus(message,blocked=false) {
    const total = [...selected.values()].reduce((a,b) => a+b,0);
    $$('#allocation-rows button').forEach(b => {
      const active=selected.has(b.dataset.key);
      b.setAttribute('aria-pressed',String(active));b.textContent=active?'✓':'○';
    });
    $('#selection-count').textContent = `${selected.size} / 3 pairs selected`;
    $('#passenger-count').textContent = total.toLocaleString('en-CA');
    $('#allocation-message').textContent = message || (selected.size === 3 ? 'Try swapping a pair. Can you help more passengers?' : 'Select a cell. See the expected passengers on the left.');
    $('.allocation-demo').classList.toggle('blocked',blocked);
  }
  function row(values) {
    const tr = document.createElement('tr');
    values.forEach(value => {const td = document.createElement('td');td.textContent = value;tr.append(td);});
    return tr;
  }
  function delayLog() {
    D.logs.forEach(log => {
      const description = log.code_description.toLowerCase().replace(/^./,c=>c.toUpperCase());
      $('#log-rows').append(row([log.Date,log.Time,log.station,description,log['Min Delay']]));
    });
    $('#data-count').textContent = D.log_count.toLocaleString('en-CA');
  }
  let tokenStep = 0;
  function dataReading() {
    D.logs.forEach(log=>{
      const description=log.code_description.toLowerCase().replace(/^./,c=>c.toUpperCase());
      $('#reading-rows').append(row([`${log.Date} ${log.Time}`,log.station,description,log['Min Delay']]));
    });
    $('#audit-missing').textContent=D.exploration.missing_core;
    $('#audit-duplicates').textContent=D.exploration.extra_duplicate_rows;
    $('#audit-range').textContent=`Longest recorded delay: ${D.exploration.max_minutes} min. Investigate before changing it.`;
  }
  function exploration() {
    const examples={
      columns:'Explain every column in the attached TTC delay CSV in plain language. Return a table with each column’s name, meaning, and unit. Flag any uncertain meanings for verification.',
      rows:'Count the rows in the attached TTC delay CSV. Return the count in one sentence. Exclude the header and count every data row without filtering.',
      stations:'Count the distinct stations using the lowercase station column in the attached TTC CSV. Return the count and an alphabetical station list. Count each station name once and report any blank values separately.',
    };
    function show(name) {
      $$('#hands-on .explore-tab').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.explore===name)));
      $('#analysis-prompt').textContent=examples[name];
      $('#copy-prompt-status').textContent='';
    }
    $$('#hands-on .explore-tab').forEach(button=>button.addEventListener('click',()=>show(button.dataset.explore)));
    $('#copy-analysis-prompt').addEventListener('click',async()=>{
      const prompt=$('#analysis-prompt');
      try {
        if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(prompt.textContent);
        $('#copy-prompt-status').textContent='Copied.';
      } catch {
        const range=document.createRange();range.selectNodeContents(prompt);
        const selection=getSelection();selection.removeAllRanges();selection.addRange(range);
        $('#copy-prompt-status').textContent='Text selected. Press ⌘C or Ctrl+C.';
      }
    });
    show('columns');
  }
  function stationCharts() {
    const values=D.exploration.station_minutes,total=D.exploration.total_minutes;
    const colors=['#267f77','#c67d42','#226a85','#65a59c','#e1a574','#528fa6','#174f4a','#96552d','#16465a','#93bfb8','#e9c39f','#8cb5c4','#3a6661','#ad8a64','#527384'];
    const prompts={
      bar:'Draw a bar plot that sums the delay minutes of all events at each station. Use different colors.',
      pie:'Draw a pie chart that sums the delay minutes of all events at each station and shows each station’s share. Show percentages and use different colors.'
    };
    const svg=$('#station-chart');
    function element(tag,attrs={},text) {
      const node=document.createElementNS('http://www.w3.org/2000/svg',tag);
      Object.entries(attrs).forEach(([key,value])=>node.setAttribute(key,value));
      if(text!==undefined)node.textContent=text;
      svg.append(node);return node;
    }
    function show(kind) {
      $('#station-example-result').classList.add('example-concealed');
      $('#station-example-result').setAttribute('aria-hidden','true');
      $('#station-example-result').inert=true;
      $('#show-station-example').hidden=false;
      $('#show-station-example').setAttribute('aria-expanded','false');
      $$('.station-chart-tab').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.chart===kind)));
      $('#station-chart-prompt').textContent=prompts[kind];$('#station-copy-status').textContent='';
      svg.replaceChildren();svg.dataset.chart=kind;
      element('title',{id:'station-chart-title'},kind==='bar'?'Total recorded delay minutes by station':'Share of recorded delay minutes by station');
      element('desc',{id:'station-chart-desc'},`Total: ${total} recorded delay minutes. `+values.map(v=>`${v.label}: ${v.minutes} minutes`).join('; '));
      if(kind==='bar') {
        const max=Math.ceil(values[0].minutes/200)*200,x0=145,width=450;
        for(let tick=0;tick<=max;tick+=200) {
          const x=x0+tick/max*width;
          element('line',{x1:x,y1:10,x2:x,y2:268,stroke:'#e1e9ed'});
          element('text',{x,y:286,'text-anchor':'middle'},tick);
        }
        values.forEach((v,i)=>{
          const y=10+i*17;
          element('text',{x:x0-10,y:y+12,'text-anchor':'end'},v.label);
          const bar=element('rect',{x:x0,y,width:v.minutes/max*width,height:13,fill:i===0?'#c67d42':'#267f77','data-minutes':v.minutes,'data-station':v.label,class:'station-bar'});
          const title=document.createElementNS(svg.namespaceURI,'title');title.textContent=`${v.label}: ${v.minutes} minutes`;bar.append(title);
          element('text',{x:x0+v.minutes/max*width+6,y:y+12},v.minutes);
        });
        element('text',{x:370,y:307,'text-anchor':'middle'},'Total recorded delay (minutes)');
      } else {
        let angle=-Math.PI/2;
        const labels=[];
        values.forEach((v,i)=>{
          const next=angle+v.minutes/total*Math.PI*2,r=110,cx=180,cy=145;
          const p1=[cx+r*Math.cos(angle),cy+r*Math.sin(angle)],p2=[cx+r*Math.cos(next),cy+r*Math.sin(next)];
          const slice=element('path',{d:`M${cx},${cy} L${p1} A${r},${r} 0 ${next-angle>Math.PI?1:0} 1 ${p2} Z`,fill:colors[i],stroke:'#fff','stroke-width':1.5,'data-minutes':v.minutes,'data-station':v.label,class:'station-slice'});
          const title=document.createElementNS(svg.namespaceURI,'title');title.textContent=`${v.label}: ${v.minutes} minutes (${(v.minutes/total*100).toFixed(1)}%)`;slice.append(title);
          const mid=(angle+next)/2;
          labels.push({station:v.label,percentage:`${(v.minutes/total*100).toFixed(1)}%`,right:Math.cos(mid)>=0,x:cx+r*Math.cos(mid),y:cy+r*Math.sin(mid),labelY:cy+(r+12)*Math.sin(mid)});
          element('rect',{x:390,y:15+i*18,width:11,height:11,fill:colors[i]});
          element('text',{x:410,y:25+i*18},v.label);
          angle=next;
        });
        // Separate nearby labels while retaining every station, including small slices.
        [false,true].forEach(right=>{
          const side=labels.filter(label=>label.right===right).sort((a,b)=>a.labelY-b.labelY);
          side.forEach((label,i)=>{label.labelY=Math.max(label.labelY,i?side[i-1].labelY+18:18);});
          for(let i=side.length-1;i>=0;i--)side[i].labelY=Math.min(side[i].labelY,i===side.length-1?272:side[i+1].labelY-18);
          side.forEach(label=>{
            element('polyline',{points:`${label.x},${label.y} ${right?302:58},${label.labelY} ${right?307:53},${label.labelY}`,fill:'none',stroke:'#93a5ae','stroke-width':1});
            element('text',{x:right?313:47,y:label.labelY+4,'text-anchor':right?'start':'end',class:'pie-percentage','data-station':label.station},label.percentage);
          });
        });
        element('text',{x:180,y:300,'text-anchor':'middle'},`${total.toLocaleString('en-CA')} recorded minutes`);
      }
      $('#station-chart-caption').textContent=kind==='bar'?`Total: ${total.toLocaleString('en-CA')} recorded minutes. Bars make station comparisons easier.`:'All 15 stations share the same total. Small slices are harder to compare.';
    }
    $$('.station-chart-tab').forEach(button=>button.addEventListener('click',()=>show(button.dataset.chart)));
    $('#show-station-example').addEventListener('click',()=>{
      $('#station-example-result').classList.remove('example-concealed');
      $('#station-example-result').setAttribute('aria-hidden','false');
      $('#station-example-result').inert=false;
      $('#show-station-example').setAttribute('aria-expanded','true');
      $('#show-station-example').hidden=true;
    });
    $('#copy-station-prompt').addEventListener('click',async()=>{
      const prompt=$('#station-chart-prompt');
      try {
        if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(prompt.textContent);$('#station-copy-status').textContent='Copied.';
      } catch {
        const range=document.createRange();range.selectNodeContents(prompt);
        const selection=getSelection();selection.removeAllRanges();selection.addRange(range);
        $('#station-copy-status').textContent='Text selected. Press ⌘C or Ctrl+C.';
      }
    });
    show('bar');
  }
  const tokenSets = [
    [['five',58],['two',27],['ten',15]],
    [['minutes',85],['seconds',10],['hours',5]],
    [['.',76],[',',18],['and',6]],
  ];
  const tokens = [' five',' minutes','.'];
  let networkRun = 0;
  let networkRunning = false;
  let networkShown = false;
  function neuralNetwork() {
    const svg=$('#llm-network');
    const layers=[
      {x:20,ys:[25,50,75],color:'#267f77'},
      {x:73,ys:[13,38,63,88],color:'#3d8dab'},
      {x:127,ys:[13,38,63,88],color:'#8d79b5'},
      {x:180,ys:[25,50,75],color:'#cf8854'},
    ];
    function shape(tag,attributes){
      const element=document.createElementNS('http://www.w3.org/2000/svg',tag);
      Object.entries(attributes).forEach(([key,value])=>element.setAttribute(key,value));
      svg.append(element);return element;
    }
    layers.forEach(layer=>shape('rect',{x:layer.x-13,y:1,width:26,height:99,rx:13,class:'network-layer',style:`--layer-color:${layer.color}`}));
    layers.slice(0,-1).forEach((layer,index)=>{
      const next=layers[index+1];
      layer.ys.forEach((y,from)=>next.ys.forEach((toY,to)=>{
        const d=`M${layer.x} ${y} L${next.x} ${toY}`;
        shape('path',{d,class:'network-wire'});
        if(to===(from+index)%next.ys.length || (from===1 && to===2)) {
          shape('path',{d,pathLength:1,class:'network-signal',style:`--signal-color:${next.color};--activation-delay:${index*.23+.08}s`});
        }
      }));
    });
    layers.forEach((layer,index)=>layer.ys.forEach((y,node)=>shape('circle',{
      cx:layer.x,cy:y,r:5.5,class:'network-node',
      style:`--node-color:${layer.color};--activation-delay:${index*.23+node*.025}s`,
    })));
    shape('text',{x:100,y:121,class:'network-label'}).textContent='LLM';
  }
  function stopNetwork() {
    networkRun++;
    const wasRunning=networkRunning;
    networkRunning=false;
    $('.model-symbol').classList.remove('network-active');
    $('#llm').classList.remove('network-pending');
    $('.prediction-stage').setAttribute('aria-busy','false');
    if(wasRunning)renderTokens();
  }
  function activateNetwork(onComplete=()=>{}) {
    stopNetwork();
    const run=networkRun;
    networkRunning=true;
    $('#llm').classList.add('network-pending');
    $('.prediction-stage').setAttribute('aria-busy','true');
    $('#generate-token').disabled=true;
    $('#token-status').textContent='Computing the next prediction…';
    function complete() {
      if(run!==networkRun)return;
      networkRunning=false;
      $('.model-symbol').classList.remove('network-active');
      onComplete();
      renderTokens();
      $('#llm').classList.remove('network-pending');
      $('.prediction-stage').setAttribute('aria-busy','false');
    }
    if(matchMedia('(prefers-reduced-motion: reduce)').matches){complete();return;}
    const model=$('.model-symbol');
    void model.offsetWidth;
    model.classList.add('network-active');
    const animations=model.getAnimations({subtree:true});
    Promise.all(animations.map(animation=>animation.finished)).then(complete,()=>{});
  }
  function renderTokens() {
    const context=$('#token-context');context.textContent='The next train arrives in';
    tokens.slice(0,tokenStep).forEach(token => {const span=document.createElement('span');span.className='generated-token';span.textContent=token;context.append(span);});
    const options=$('#token-options');options.replaceChildren();
    // Keep the distribution that produced the token just appended on screen.
    tokenSets[Math.max(0,tokenStep-1)].forEach(([text,probability]) => {
      const option=document.createElement('div');option.className='token-option';
      const name=document.createElement('span');name.className='token-name';name.textContent=text;
      const track=document.createElement('span');track.className='token-bar';track.setAttribute('aria-hidden','true');
      const bar=document.createElement('span');bar.style.width=probability+'%';track.append(bar);
      const probabilityLabel=document.createElement('span');probabilityLabel.className='token-probability';probabilityLabel.textContent=probability+'%';
      option.append(name,track,probabilityLabel);options.append(option);
    });
    $('#generate-token').disabled=networkRunning || tokenStep===3;
    $('#token-heading').textContent=tokenStep===3?'Final token selected':'Next-token prediction';
    $('#token-status').textContent=tokenStep===3?'Sentence complete. Reset to replay.':tokenStep>0?'The longer context changes the next prediction.':'Try completing the sentence.';
  }
  function exercises() {
    const feedback={
      invitation:{one:'A good fit. Check the summary against the invitation.',process:'Useful if details conflict. A simple invitation usually needs only a quick check.'},
      ttc:{one:'Useful for a first draft. Inspect the data and predictions before choosing three pairs.',process:'A good fit. Check the data, test predictions, and compare station–time selections.'},
      competition:{one:'Useful for brainstorming. Distinctive framing and validation still need attention.',process:'A good fit. Your questions, assumptions, and evidence can distinguish the result.'},
    };
    $$('.exercise').forEach(exercise => {
      exercise.querySelectorAll('button').forEach(button => {
        button.setAttribute('aria-pressed','false');
        button.addEventListener('click',() => {
          exercise.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
          exercise.querySelector('.exercise-feedback').textContent=feedback[exercise.dataset.case][button.dataset.choice];
        });
      });
    });
    $('#back-to-comparison').addEventListener('click',()=>Reveal.prevFragment());
  }
  function sync() {
    if(Reveal.isPrintView())return;
    const slide=Reveal.getCurrentSlide();
    if(slide.id==='understand-data') {
      slide.dataset.readingStep=slide.querySelector('.reading-step[data-fragment-index="2"].visible')?'checks':slide.querySelector('.reading-step[data-fragment-index="1"].visible')?'units':'row';
    }
    const showNetwork=slide.id==='llm' && $('.model-stage').classList.contains('visible');
    if(showNetwork && !networkShown)activateNetwork(()=>{if(tokenStep===0)tokenStep=1;});
    if(!showNetwork)stopNetwork();
    networkShown=showNetwork;
    if(slide.id==='one-shot') {
      $$('.comparison-table tbody tr').forEach(row=>{
        row.setAttribute('aria-hidden',String(!row.classList.contains('visible')));
      });
      const active=Boolean(slide.querySelector('.step-marker.visible'));
      slide.dataset.step=active?'1':'0';
      $('.exercise-panel').setAttribute('aria-hidden',String(!active));
      $('.exercise-panel').inert=!active;
      $('.comparison-panel').setAttribute('aria-hidden',String(active));
      if(!active && $('.exercise-panel').contains(document.activeElement)) document.activeElement.blur();
    }
  }
  function initialize() {
    footer();contentsMenu();toolsMenu();allocation();delayLog();dataReading();exploration();stationCharts();neuralNetwork();renderTokens();exercises();window.initializeLaterSlides();
    $('#generate-token').addEventListener('click',()=>{if(tokenStep<3 && !networkRunning)activateNetwork(()=>{tokenStep++;});});
    $('#reset-tokens').addEventListener('click',()=>{stopNetwork();tokenStep=0;renderTokens();});
    Reveal.configure({pdfSeparateFragments:false,keyboardCondition:event=>!event.target.closest('button,input,textarea,select,a')});
    Reveal.on('slidechanged',sync);Reveal.on('fragmentshown',sync);Reveal.on('fragmenthidden',sync);
    $('.slides').addEventListener('click',event=>{
      if(event.button!==0 || event.target.closest('a,button,input,textarea,select,summary,.notes') || getSelection()?.toString() || Reveal.isOverview())return;
      Reveal.next();
    });
    // Restore focus to the slide canvas after pointer use so arrow navigation resumes.
    $$('.slides button').forEach(b=>b.addEventListener('pointerup',()=>b.blur()));
    sync();preparePrintView();window.SLIDES_READY=true;
  }
  if(typeof Reveal!=='undefined') {if(Reveal.isReady())initialize();else Reveal.on('ready',initialize);}
})();
