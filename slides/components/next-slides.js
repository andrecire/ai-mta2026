(() => {
  'use strict';
  const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
  const D=window.WORKSHOP_DATA;
  function svgElement(root,tag,attrs={},text) {
    const node=document.createElementNS('http://www.w3.org/2000/svg',tag);
    Object.entries(attrs).forEach(([key,value])=>node.setAttribute(key,value));
    if(text!==undefined)node.textContent=text;
    root.append(node);return node;
  }
  function histograms() {
    const svg=$('#weekday-histograms'),colors=['#267f77','#c67d42','#226a85','#65a59c','#a4592f'];
    svgElement(svg,'title',{id:'weekday-hist-title'},'Recorded delay-duration distributions by weekday');
    svgElement(svg,'desc',{id:'weekday-hist-desc'},'Five histograms of positive-delay durations, with identical one-minute bins and shared percentage axes.');
    const ymax=Math.ceil(Math.max(...D.weekday_histograms.flatMap(day=>day.bins.map(count=>100*count/day.count)))/10)*10;
    D.weekday_histograms.forEach((day,i)=>{
      const ox=(i%3)*220,oy=Math.floor(i/3)*150;
      const group=svgElement(svg,'g',{'data-weekday':day.day,'data-count':day.count});
      svgElement(group,'text',{x:ox+10,y:oy+18,class:'hist-day'},`${day.day} · n=${day.count}`);
      const x0=ox+30,y0=oy+112,w=175,h=75;
      [0,ymax/2,ymax].forEach(tick=>{
        const y=y0-tick/ymax*h;
        svgElement(group,'line',{x1:x0,y1:y,x2:x0+w,y2:y,stroke:'#dce4e9','stroke-width':1});
        svgElement(group,'text',{x:x0-5,y:y+4,'text-anchor':'end',class:'hist-tick'},tick);
      });
      day.bins.forEach((count,j)=>{
        const height=100*count/day.count/ymax*h;
        const bar=svgElement(group,'rect',{x:x0+j*w/10,y:y0-height,width:w/10,height,fill:colors[i],stroke:'#fff','stroke-width':.4,class:'weekday-bin','data-bin':j,'data-count':count});
        svgElement(bar,'title',{},`${day.day}, ${j+1} minutes: ${count} entries (${(count/day.count*100).toFixed(1)}%)`);
      });
      [1,3,5,7,9].forEach(tick=>svgElement(group,'text',{x:x0+(tick-.5)/10*w,y:y0+17,'text-anchor':'middle',class:'hist-tick'},tick));
    });
    svgElement(svg,'text',{x:450,y:190,class:'hist-guide'},'Same scale for every day');
    svgElement(svg,'text',{x:450,y:216,class:'hist-tick'},'Horizontal: delay minutes');
    svgElement(svg,'text',{x:450,y:238,class:'hist-tick'},'Vertical: % of weekday entries');
    svgElement(svg,'text',{x:330,y:325,'text-anchor':'middle',class:'hist-axis'},'Recorded delay per entry (minutes)');
  }
  function scatter() {
    const svg=$('#delay-gap-scatter'),points=D.scatter.points;
    $('#scatter-correlation-value').textContent=`Pearson r = ${D.scatter.pearson_r.toFixed(3)} · strong positive association`;
    function draw(limit) {
      svg.replaceChildren();
      const visible=points.filter(p=>p.delay<=limit&&p.gap<=limit);
      svgElement(svg,'title',{id:'scatter-title'},'Recorded delay minutes and time between trains');
      svgElement(svg,'desc',{id:'scatter-desc'},`${visible.length} of ${points.length} entries within 0–${limit} minutes on both axes. Overlapping dots share coordinates. Full-sample Pearson correlation ${D.scatter.pearson_r.toFixed(3)}.`);
      const x0=65,y0=235,w=550,h=210;
      const ticks=limit===150?[0,50,100,150]:[0,5,10,15,20];
      ticks.forEach(t=>{
        const x=x0+t/limit*w,y=y0-t/limit*h;
        svgElement(svg,'line',{x1:x,y1:y0-h,x2:x,y2:y0,stroke:'#dce4e9'});
        svgElement(svg,'line',{x1:x0,y1:y,x2:x0+w,y2:y,stroke:'#dce4e9'});
        svgElement(svg,'text',{x,y:y0+20,'text-anchor':'middle',class:'scatter-tick'},t);
        svgElement(svg,'text',{x:x0-10,y:y+5,'text-anchor':'end',class:'scatter-tick'},t);
      });
      visible.forEach(p=>{
        const dot=svgElement(svg,'circle',{cx:x0+p.delay/limit*w,cy:y0-p.gap/limit*h,r:3.5,fill:'#267f77','fill-opacity':.32,class:'scatter-point','data-delay':p.delay,'data-gap':p.gap});
        svgElement(dot,'title',{},`Delay: ${p.delay} min · Gap: ${p.gap} min`);
      });
      svgElement(svg,'text',{x:340,y:283,'text-anchor':'middle',class:'scatter-axis'},'Recorded delay (minutes)');
      svgElement(svg,'text',{transform:'translate(17 130) rotate(-90)','text-anchor':'middle',class:'scatter-axis'},'Time between trains (minutes)');
      $('#scatter-view-note').textContent=limit===150?`${points.length} entries · Dots can overlap`:`${visible.length} in view · ${points.length-visible.length} outside · r still uses all ${points.length}`;
      $$('[data-scatter-limit]').forEach(button=>button.setAttribute('aria-pressed',String(Number(button.dataset.scatterLimit)===limit)));
    }
    $$('[data-scatter-limit]').forEach(button=>button.addEventListener('click',()=>draw(Number(button.dataset.scatterLimit))));
    draw(150);
  }
  function network() {
    const svg=$('#prediction-network'),xs=[24,77,133,190],ys=[[25,65],[15,45,75],[15,45,75],[30,60]];
    xs.slice(0,-1).forEach((x,i)=>ys[i].forEach(y=>ys[i+1].forEach(z=>svgElement(svg,'line',{x1:x,y1:y,x2:xs[i+1],y2:z,stroke:'#b9d4d1','stroke-width':1.3}))));
    xs.forEach((x,i)=>ys[i].forEach(y=>svgElement(svg,'circle',{cx:x,cy:y,r:6,fill:i%2?'#c67d42':'#267f77',class:'prediction-node',style:`--node-delay:${i*.2}s`})));
  }
  function movingAverage() {
    const svg=$('#moving-average-chart'),data=D.moving_average;
    const labels=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct'];
    const x=i=>65+i*59,y=v=>235-v/2.5*185;
    svgElement(svg,'title',{id:'moving-average-title'},'Three-month moving average predicts October');
    svgElement(svg,'desc',{id:'moving-average-desc'},`Bloor-Yonge 07–09. Actual monthly average minutes per weekday window from January through September 2025. The July–September average predicts ${data.forecast.toFixed(2)} minutes for October.`);
    svgElement(svg,'rect',{x:x(6)-28,y:40,width:174,height:195,fill:'#eaf0f6',rx:4});
    svgElement(svg,'text',{x:x(7),y:25,'text-anchor':'middle',class:'moving-annotation'},'Average these three');
    [0,.5,1,1.5,2,2.5].forEach(t=>{
      svgElement(svg,'line',{x1:65,y1:y(t),x2:610,y2:y(t),stroke:'#dce4e9'});
      svgElement(svg,'text',{x:55,y:y(t)+4,'text-anchor':'end',class:'moving-tick'},t);
    });
    labels.forEach((label,i)=>svgElement(svg,'text',{x:x(i),y:259,'text-anchor':'middle',class:'moving-tick'},label));
    svgElement(svg,'text',{transform:'translate(17 145) rotate(-90)','text-anchor':'middle',class:'moving-axis'},'Minutes per weekday window');
    svgElement(svg,'path',{d:data.months.map((r,i)=>`${i?'L':'M'}${x(i)} ${y(r.mean)}`).join(' '),fill:'none',stroke:'#267f77','stroke-width':3});
    data.months.forEach((r,i)=>{
      const dot=svgElement(svg,'circle',{cx:x(i),cy:y(r.mean),r:5,fill:'#267f77',class:'moving-observation','data-month':r.month,'data-mean':r.mean});
      svgElement(dot,'title',{},`${r.month}: ${r.mean.toFixed(3)} minutes per window (${r.days} weekdays)`);
    });
    svgElement(svg,'line',{x1:x(8),y1:y(data.months[8].mean),x2:x(9),y2:y(data.forecast),stroke:'#c67d42','stroke-width':3,'stroke-dasharray':'6 5'});
    svgElement(svg,'circle',{cx:x(9),cy:y(data.forecast),r:6,fill:'#c67d42',id:'moving-forecast','data-value':data.forecast});
    svgElement(svg,'text',{x:x(9),y:y(data.forecast)-15,'text-anchor':'middle',class:'moving-forecast-label'},data.forecast.toFixed(2));
    svgElement(svg,'text',{x:200,y:294,class:'moving-legend'},'Teal: observed');
    svgElement(svg,'text',{x:375,y:294,class:'moving-legend forecast-legend'},'Orange: forecast');
    $('#moving-average-equation').textContent=`(${data.months.slice(-3).map(r=>r.mean.toFixed(2)).join(' + ')}) ÷ 3 ≈ ${data.forecast.toFixed(2)}`;
  }
  function csvDownloads() {
    D.downloads.forEach(file=>{
      const link=$(`#${file.id}`);
      // Keep shareable relative file links online; preserve single-file offline downloads.
      if(location.protocol==='file:') link.href=URL.createObjectURL(new Blob([file.csv],{type:'text/csv;charset=utf-8'}));
      link.download=file.filename;
    });
  }
  function planner() {
    const keys=[['Bloor-Yonge','07:00-09:00'],['Bloor-Yonge','16:00-18:00'],['St George','12:00-14:00'],['Wilson','07:00-09:00'],['Eglinton','16:00-18:00'],['Kipling','16:00-18:00']];
    const candidates=keys.map(([station,window])=>D.window_baselines.find(row=>row.station===station&&row.window===window));
    const selected=new Set(),buttons=[];
    const score=row=>row.mean_minutes*10;
    const best=candidates.map((row,i)=>({i,value:score(row)})).sort((a,b)=>b.value-a.value).slice(0,3);
    function update(message='') {
      buttons.forEach((button,i)=>button.setAttribute('aria-pressed',String(selected.has(i))));
      $('#planner-count').textContent=`${selected.size} / 3 selected`;
      $('#planner-total').textContent=[...selected].reduce((total,i)=>total+score(candidates[i]),0).toFixed(1);
      $('#planner-message').textContent=message;
      $('#planner-benchmark').textContent=`Best 3: ${best.reduce((sum,row)=>sum+row.value,0).toFixed(1)}`;
    }
    candidates.forEach((row,i)=>{
      const button=document.createElement('button');button.type='button';button.className='planner-pair';button.dataset.score=score(row);
      const label=document.createElement('span'),value=document.createElement('strong');
      label.textContent=`${row.station} · ${row.window.slice(0,2)}–${row.window.slice(6,8)}`;value.textContent=score(row).toFixed(1);
      button.append(label,value);button.addEventListener('click',()=>{
        if(selected.has(i))selected.delete(i);else if(selected.size<3)selected.add(i);else return update('Three selected. Remove one to try another.');
        update();
      });buttons.push(button);$('#planner-candidates').append(button);
    });
    $('#planner-reset').addEventListener('click',()=>{selected.clear();update();});
    $('#planner-best').addEventListener('click',()=>{selected.clear();best.forEach(row=>selected.add(row.i));update('Best three within these six examples.');});
    update();
  }
  window.initializeLaterSlides=()=>{
    histograms();scatter();network();movingAverage();csvDownloads();planner();
    $$('[data-copy-target]').forEach(button=>button.addEventListener('click',async()=>{
      const prompt=$(`#${button.dataset.copyTarget}`),status=$(`#${button.dataset.copyStatus}`);
      try {
        if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(prompt.textContent);status.textContent='Copied.';
      } catch {
        const range=document.createRange();range.selectNodeContents(prompt);const selection=getSelection();selection.removeAllRanges();selection.addRange(range);
        status.textContent='Text selected. Press ⌘C or Ctrl+C.';
      }
    }));
    $$('[data-reveal-target]').forEach(button=>button.addEventListener('click',()=>{
      const result=$(`#${button.dataset.revealTarget}`);result.classList.remove('example-concealed');result.setAttribute('aria-hidden','false');result.inert=false;button.hidden=true;
    }));
  };
})();
