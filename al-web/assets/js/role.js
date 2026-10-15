(function(){
var K="al-role",root=document.documentElement,r="bank";
try{r=localStorage.getItem(K)||"bank"}catch(e){}
root.dataset.role=r;
document.addEventListener("DOMContentLoaded",function(){
 var bs=document.querySelectorAll("[data-role-btn]");
 function paint(){bs.forEach(function(b){b.setAttribute("aria-pressed",b.dataset.roleBtn===root.dataset.role)})}
 bs.forEach(function(b){b.addEventListener("click",function(){
  root.dataset.role=b.dataset.roleBtn;try{localStorage.setItem(K,root.dataset.role)}catch(e){}paint()})});
 paint();
});})();
