document.addEventListener("DOMContentLoaded",function(){
var ir=document.getElementById("ir"),hm=document.getElementById("hm");
function set(id,v){document.getElementById(id).textContent=v}
function run(){
 var bps=+ir.value,hpi=+hm.value;
 var dr=bps/100*0.8+hpi/5*0.35;
 var ltv=68.4/(1-hpi/100)+bps*0.003;
 var br=Math.max(0,Math.min(42,Math.round((ltv-69)*1.7)));
 set("o-bps","+"+bps+" bps");set("o-hpi","-"+hpi+"%");
 set("o-dr","+"+dr.toFixed(1)+" pts");set("o-ltv",ltv.toFixed(1)+"%");
 set("o-br",br+" of 42");set("o-rate",(3.85+bps/100).toFixed(2)+"%");
 var c=function(v,a,b){return v>b?"var(--rose)":v>a?"var(--am)":"var(--tx)"};
 document.getElementById("o-dr").style.color=c(dr,1,2.5);
 document.getElementById("o-ltv").style.color=c(ltv,70,78);
 document.getElementById("o-br").style.color=c(br,3,10);
}
ir.addEventListener("input",run);hm.addEventListener("input",run);run();
});
