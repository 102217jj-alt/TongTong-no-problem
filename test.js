var document = {getElementById:()=>({ style:{}, classList:{add:()=>{},remove:()=>{}} }), querySelectorAll:()=>[], documentElement:{style:{setProperty:()=>{}}}, createElement:()=>({style:{},classList:{add:()=>{},remove:()=>{}},appendChild:()=>{}}) };
var window = {addEventListener:()=>{}, location:{href:''}, AudioContext:function(){this.state='running';this.resume=()=>{}} };
var localStorage = {getItem:()=>null, setItem:()=>{}};
var bootstrap = {Modal:class{show(){}hide(){}}};
function Audio(){this.play=async()=>{};this.pause=()=>{}}
var fetch = async()=>({json:async()=>({})});
var setInterval=()=>{}, setTimeout=()=>{}, requestAnimationFrame=()=>{}, cancelAnimationFrame=()=>{};

        window.onerror = function(message, source, lineno, colno, error) {
            alert("網頁發生錯誤：\n" + message + "\n行數：" + lineno + "\n請截圖給通通的開發者！");
        };
    