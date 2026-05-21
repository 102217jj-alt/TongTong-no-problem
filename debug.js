try {
  var window = {}; var document = { getElementById: ()=>({}), querySelectorAll: ()=>[], createElement: ()=>({ style: {}, classList: { add: ()=>{}, remove: ()=>{} } }) };
  var localStorage = { getItem: ()=>null, setItem: ()=>{} };
  var bootstrap = { Modal: class { show(){} hide(){} } };

        // DOM Elements
        const chatContainer = document.getElementById('chat-container');
        const textInput = document.getElementById('text-input');
        const sendBtn = document.getElementById('send-btn');
        const micBtn = document.getElementById('mic-btn');
        const inputArea = document.getElementById('input-area');
        const voiceSelect = document.getElementById('voice-select');
        const quickActions = document.getElementById('quick-actions');
        const modeDropdown = document.getElementById('mode-dropdown');
        const btnOriginal = document.getElementById('btn-original');
        const gameDashboard = document.getElementById('game-dashboard');
        const gameBtn = document.getElementById('game-zone-btn');
        const controlsArea = document.getElementById('controls-area');

        // State Variables
        let currentMode = '通通沒問題', currentAudio = null, nextAudioToPlay = null, isProcessing = false, abortController = null, namePromptShownForMode = null;
        let namePromptModal = null, titlePromptModal = null, sheepCountModal = null, natureSoundModal = null, questionPromptModal = null, gomokuModal = null, rpsModal = null;
        let highFiveOverlay = null, highFiveTimer = null, rpsRevealTimer = null, rpsReplyTimer = null, rpsRoundId = 0;

        // Init Voice
        const serverVoice = "female";
        voiceSelect.value = (serverVoice && serverVoice !== "None") ? serverVoice : (localStorage.getItem('tongtong_voice') || 'female');
        voiceSelect.onchange = () => localStorage.setItem('tongtong_voice', voiceSelect.value);

        const THEMES = {
            '通通沒問題': { primary: '#007bff', accent: '#333', bg: '#f8f9fa', nav: '#ffffff' },
            '好心情': { primary: '#f39c12', accent: '#333', bg: '#fff9e6', nav: '#fffcf0' },
            '神算師': { primary: '#9b59b6', accent: '#333', bg: '#f8f0ff', nav: '#fbf8ff' },
            '屬於我': { primary: '#e91e63', accent: '#333', bg: '#fff0f5', nav: '#fff8fa' },
            '去睡覺': { primary: '#34495e', accent: '#333', bg: '#f0f4f8', nav: '#f8fafd' },
            '不知道': { primary: '#1abc9c', accent: '#333', bg: '#f0fff4', nav: '#f8fffb' },
            '遊戲專區': { primary: '#2980b9', accent: '#fff', bg: '#aed6f1', nav: '#85c1e9' }
        };

        const MODE_ACTIONS = {
            '通通沒問題': ['你是誰？', '台北天氣', '現在時間', '推薦好吃的', '說個勵志名言', '查 台灣歷史'],
            '好心情': ['講個笑話', '唱首歌', '給我鼓勵', '變個魔術', '猜拳', '跟我擊掌'],
            '神算師': ['占卜運勢', '測幸運色', '算幸運數字', '問吉時', '財運', '事業運', '愛情運', '今日建議'],
            '屬於我': ['甜言蜜語', '親親', '抱抱', '土味情話', '專屬稱號', '修改稱呼'],
            '去睡覺': ['睡前故事', '數羊', '冥想引導', '大自然聲音', '晚安寄語'],
            '不知道': ['我要問問題', '不知道世界新聞', '冷知識大挑戰', '神秘驚喜盒'],
            '遊戲專區': ['五子棋', '飛鳥挑戰', '夢幻賽車手']
        };

        // --- Car Racer Game ---
        let carModalInstance = null, carCanvas = null, carCtx = null, carAnimationFrame = null;
        let carLane = 1, carTargetX = 180, carCurrentX = 180, carY = 380, carScore = 0, carSpeed = 5, carGameState = 'start';
        let carEnemies = [], carRoadOffset = 0;
        const lanesX = [60, 180, 300];

        function openCarGame() {
            const m = document.getElementById('carModal');
            if (!carModalInstance) carModalInstance = new bootstrap.Modal(m);
            carModalInstance.show();
            carCanvas = document.getElementById('carCanvas');
            carCtx = carCanvas.getContext('2d');
            carCanvas.onclick = (e) => {
                const rect = carCanvas.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                if (carGameState === 'playing') {
                    if (clickX < 120 && carLane > 0) carLane--;
                    else if (clickX > 240 && carLane < 2) carLane++;
                    carTargetX = lanesX[carLane];
                    playBeep(300, 400, 0.05);
                } else if (carGameState === 'start') {
                    handleCarInput();
                }
            };
            resetCarGame();
        }

        function closeCarGame() { if (carAnimationFrame) cancelAnimationFrame(carAnimationFrame); }
        function resetCarGame() {
            carLane = 1; carTargetX = 180; carCurrentX = 180; carScore = 0; carSpeed = 5; carGameState = 'start';
            carEnemies = []; carRoadOffset = 0;
            document.getElementById('car-score').innerText = '0';
            document.getElementById('car-start-screen').style.display = 'block';
            document.getElementById('car-over-screen').style.display = 'none';
            drawCarGame();
        }

        function handleCarInput() {
            if (carGameState === 'start') {
                carGameState = 'playing';
                document.getElementById('car-start-screen').style.display = 'none';
                carGameLoop();
            }
        }

        function carGameLoop() {
            if (carGameState !== 'playing') return;
            updateCarGame();
            drawCarGame();
            carAnimationFrame = requestAnimationFrame(carGameLoop);
        }

        function updateCarGame() {
            carRoadOffset = (carRoadOffset + carSpeed) % 80;
            carScore++;
            if (carScore % 200 === 0) carSpeed += 0.5; // 漸漸變快
            document.getElementById('car-score').innerText = Math.floor(carScore/10);

            carCurrentX += (carTargetX - carCurrentX) * 0.2;

            if (carEnemies.length === 0 || carEnemies[carEnemies.length-1].y > 200) {
                const lane = Math.floor(Math.random() * 3);
                const types = ['🚚', '🚕', '🚧', '📦'];
                carEnemies.push({ lane: lane, y: -100, type: types[Math.floor(Math.random()*types.length)] });
            }

            for (let i = carEnemies.length - 1; i >= 0; i--) {
                carEnemies[i].y += carSpeed;
                const ex = lanesX[carEnemies[i].lane];
                if (Math.abs(carCurrentX - ex) < 40 && Math.abs(carY - carEnemies[i].y) < 50) {
                    gameOverCar();
                }
                if (carEnemies[i].y > 500) carEnemies.splice(i, 1);
            }
        }

        function drawCarGame() {
            carCtx.fillStyle = '#dfe6e9'; carCtx.fillRect(0, 0, 360, 480);
            carCtx.fillStyle = '#b2bec3'; carCtx.fillRect(20, 0, 320, 480);
            carCtx.strokeStyle = '#ffffff'; carCtx.setLineDash([40, 40]); carCtx.lineDashOffset = -carRoadOffset; carCtx.lineWidth = 4;
            [120, 240].forEach(x => { carCtx.beginPath(); carCtx.moveTo(x, 0); carCtx.lineTo(x, 480); carCtx.stroke(); });
            carCtx.setLineDash([]); carCtx.font = "50px serif"; carCtx.textAlign = 'center'; carCtx.textBaseline = 'middle';
            carEnemies.forEach(e => { carCtx.fillText(e.type, lanesX[e.lane], e.y); });
            carCtx.fillText('🚗', carCurrentX, carY);
        }

        function gameOverCar() {
            carGameState = 'over'; cancelAnimationFrame(carAnimationFrame); playRpsTone('lose');
            document.getElementById('car-final-score').innerText = Math.floor(carScore/10);
            document.getElementById('car-over-screen').style.display = 'block';
            let msg = carScore < 500 ? "哎呀！通通覺得你還要再練練車喔 🏎️💨" : `太強了！你跑了 ${Math.floor(carScore/10)} 公尺，是夢幻賽車手！✨🏆`;
            sendMessage(`[RESULT]${msg}`, true);
        }

        // --- Flying Bird Game ---
        let birdModalInstance = null, birdCanvas = null, birdCtx = null, birdAnimationFrame = null, birdX = 50, birdY = 200, birdVelocity = 0, birdGravity = 0.4, birdLift = -6, birdPipes = [], birdPipeWidth = 50, birdPipeGap = 150, birdPipeSpeed = 2, birdScore = 0, birdGameState = 'start';
        function openBirdGame() { 
            const m = document.getElementById('birdModal'); 
            if (!birdModalInstance) birdModalInstance = new bootstrap.Modal(m); 
            birdModalInstance.show(); 
            birdCanvas = document.getElementById('birdCanvas'); 
            birdCtx = birdCanvas.getContext('2d'); 
            birdCanvas.onclick = handleBirdInput; 
            resetBirdGame(); 
        }
        function closeBirdGame() { if (birdAnimationFrame) cancelAnimationFrame(birdAnimationFrame); }
        function resetBirdGame() { 
            birdY = 200; birdVelocity = 0; birdPipes = []; birdScore = 0; birdGameState = 'start'; 
            document.getElementById('bird-score').innerText = '0'; 
            document.getElementById('bird-start-screen').style.display = 'block'; 
            document.getElementById('bird-over-screen').style.display = 'none'; // 隱藏結束畫面
            drawBirdGame(); 
        }
        function handleBirdInput() { 
            if (birdGameState === 'start') { 
                birdGameState = 'playing'; 
                document.getElementById('bird-start-screen').style.display = 'none'; 
                birdGameLoop(); 
            } else if (birdGameState === 'playing') { 
                birdVelocity = birdLift; 
                playBeep(400, 600, 0.05); 
            } 
            // 移除 'over' 狀態下的 resetBirdGame()，改由按鈕觸發
        }
        function birdGameLoop() { if (birdGameState !== 'playing') return; updateBirdGame(); drawBirdGame(); birdAnimationFrame = requestAnimationFrame(birdGameLoop); }
        function updateBirdGame() {
            birdVelocity += birdGravity; birdY += birdVelocity;
            if (birdPipes.length === 0 || birdPipes[birdPipes.length - 1].x < 180) birdPipes.push({ x: 360, top: Math.floor(Math.random() * 250) + 50, passed: false });
            for (let i = birdPipes.length - 1; i >= 0; i--) {
                birdPipes[i].x -= birdPipeSpeed;
                if ((birdX + 35 > birdPipes[i].x && birdX + 5 < birdPipes[i].x + 50 && (birdY + 5 < birdPipes[i].top || birdY + 35 > birdPipes[i].top + 150)) || birdY < 0 || birdY + 40 > 500) gameOverBird();
                if (!birdPipes[i].passed && birdPipes[i].x + 50 < birdX) { birdPipes[i].passed = true; birdScore++; document.getElementById('bird-score').innerText = birdScore; playBeep(800, 1000, 0.1); }
                if (birdPipes[i].x + 50 < 0) birdPipes.splice(i, 1);
            }
        }
        function drawBirdGame() { 
            birdCtx.clearRect(0, 0, 360, 480); 
            birdPipes.forEach(p => { 
                birdCtx.fillStyle = '#55efc4'; // 明亮的可愛綠色
                birdCtx.fillRect(p.x, 0, 50, p.top); 
                birdCtx.fillRect(p.x, p.top + 150, 50, 480); 
                birdCtx.strokeStyle = '#ffffff'; 
                birdCtx.lineWidth = 3;
                birdCtx.strokeRect(p.x, 0, 50, p.top); 
                birdCtx.strokeRect(p.x, p.top + 150, 50, 480); 
            }); 
            if (birdGameState !== 'start') {
                birdCtx.save();
                birdCtx.translate(birdX + 20, birdY + 20);
                birdCtx.rotate(Math.min(Math.PI / 4, Math.max(-Math.PI / 4, (birdVelocity * 0.1))));
                birdCtx.font = "40px serif"; 
                birdCtx.textBaseline = 'middle'; 
                birdCtx.textAlign = 'center';
                birdCtx.fillText('🐦', 0, 0); 
                birdCtx.restore();
            }
        }
        function gameOverBird() { 
            birdGameState = 'over'; 
            cancelAnimationFrame(birdAnimationFrame); 
            playRpsTone('lose'); 
            
            // 顯示結束畫面與分數
            document.getElementById('bird-final-score').innerText = birdScore;
            document.getElementById('bird-over-screen').style.display = 'block';
            
            let msg = birdScore === 0 ? "哎呀！通通覺得你可能還沒睡醒喔～💤" : (birdScore < 5 ? `不錯喔！拿到 ${birdScore} 分，加油！💪` : `太神啦！拿到 ${birdScore} 分！✨🏆`); 
            sendMessage(`[RESULT]${msg}`, true); 
        }

        // --- Interactions & Animations ---
        function clearRpsTimers() { if (rpsRevealTimer) clearTimeout(rpsRevealTimer); if (rpsReplyTimer) clearTimeout(rpsReplyTimer); }
        function playRpsTone(type) { const c = getCtx(), n = c.currentTime; if (type === 'win') [523, 659, 783, 1046].forEach((f, i) => playBeep(f, f, 0.1, n + i * 0.1)); else if (type === 'lose') [440, 349, 261].forEach((f, i) => playBeep(f, f * 0.8, 0.2, n + i * 0.2)); }
        function showAffectionAnimation(kind) {
            const isKiss = kind === 'kiss'; const overlay = document.createElement('div'); overlay.className = 'affection-overlay';
            overlay.innerHTML = `<div class="affection-card"><div class="affection-title">${isKiss ? '親親模式啟動' : '抱抱模式啟動'}</div><div class="emoji-stage"><div class="emoji-face left ${isKiss ? 'kiss-left' : 'hug-left'}"><span>${isKiss ? '😘' : '🤗'}</span></div><div class="emoji-face right ${isKiss ? 'kiss-right' : 'hug-right'}"><span style="display:inline-block;transform:scaleX(-1);">${isKiss ? '😘' : '🤗'}</span></div>${[1,2,3,4,5].map(i => `<div class="floating float-heart" style="left:${i*20}%; animation-delay:${i*0.2}s">❤️</div>`).join('')}</div><div class="affection-text">${isKiss ? '啾一下，甜甜的心意送給你！' : '來一個大大抱抱，暖暖抱緊你！'}</div></div>`;
            document.body.appendChild(overlay); setTimeout(() => overlay.remove(), 2000);
        }
        function triggerHighFiveCelebration() { const overlay = document.createElement('div'); overlay.className = 'highfive-overlay'; overlay.innerHTML = `<div class="highfive-card"><div class="highfive-hand left">✋</div><div class="highfive-hand right">🖐️</div><div class="highfive-burst">💥</div><div class="highfive-text">啪！擊掌成功！🤝💖</div></div>`; document.body.appendChild(overlay); playBeep(600, 200, 0.1); setTimeout(() => overlay.remove(), 1500); }
        function openRPSGame() { if (!rpsModal) rpsModal = new bootstrap.Modal(document.getElementById('rpsModal')); document.getElementById('rps-status').innerText = "通通準備好了，你呢？😏"; document.getElementById('rps-result').style.display = "none"; rpsModal.show(); }
        function playRPS(userChoice) {
            const rid = ++rpsRoundId; stopCurrentAudio(); clearRpsTimers();
            const choices = ['✊', '✌️', '🖐️'], statusP = document.getElementById('rps-status'), resultDiv = document.getElementById('rps-result');
            statusP.innerText = `你出 ${userChoice}，我出 ?`; resultDiv.style.display = "none";
            rpsRevealTimer = setTimeout(() => {
                if (rid !== rpsRoundId) return;
                const botChoice = choices[Math.floor(Math.random() * 3)];
                let outcome = "", color = "", speech = "", voice = ""; const map = {'✊':'石頭','✌️':'剪刀','🖐️':'布'};
                if (userChoice === botChoice) { outcome = "平手！😮"; color = "text-warning"; speech = `我們都出 ${userChoice}，是平手耶！`; voice = `我們都出 ${map[userChoice]}，是平手耶！`; }
                else if ((userChoice==='✊'&&botChoice==='✌️')||(userChoice==='✌️'&&botChoice==='🖐️')||(userChoice==='🖐️'&&botChoice==='✊')) { outcome = "你贏了！🎉✨"; color = "text-success"; speech = `嗚嗚，你出 ${userChoice}，我出 ${botChoice}。你贏了！`; voice = `嗚嗚，你出 ${map[userChoice]}，我出 ${map[botChoice]}。你贏過通通了！`; playRpsTone('win'); }
                else { outcome = "通通贏了！😜💖"; color = "text-danger"; speech = `嘿嘿！你出 ${userChoice}，我出 ${botChoice}。通通贏囉！`; voice = `嘿嘿！你出 ${map[userChoice]}，我出 ${map[botChoice]}。這局是通通贏囉！`; playRpsTone('lose'); }
                statusP.innerText = `你出 ${userChoice}，我出 ${botChoice}`; resultDiv.innerText = outcome; resultDiv.style.display = "block"; resultDiv.className = "mt-4 h3 fw-bold " + color;
                rpsReplyTimer = setTimeout(() => { if (rid === rpsRoundId) { if (rpsModal) rpsModal.hide(); const m = addMessage('bot', speech); fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: `[RESULT]${voice}`, mode: currentMode, voice_type: voiceSelect.value }) }).then(r => r.json()).then(d => { if (rid === rpsRoundId && d.audio_url) { attachReplayButton(m, d.audio_url); playAudioFromUrl(d.audio_url); } }); } }, 1500);
            }, 700);
        }

        // --- Core Functions ---
        function applyTheme(mode) {
            const theme = THEMES[mode] || THEMES['通通沒問題']; const root = document.documentElement;
            root.style.setProperty('--primary-color', theme.primary); root.style.setProperty('--bg-light', theme.bg); root.style.setProperty('--nav-bg', theme.nav);
            document.querySelectorAll('.custom-modal-theme').forEach(mc => { 
                mc.style.border = 'none'; // 徹底移除邊框
                const t = mc.querySelector('.modal-title'); if (t) t.style.color = theme.primary; 
            });
            document.querySelectorAll('.theme-submit-btn').forEach(b => b.style.backgroundColor = theme.primary);
        }

        function updateUIForMode(mode) {
            applyTheme(mode); const isGame = mode === '遊戲專區';
            gameBtn.style.display = isGame ? 'none' : 'flex'; chatContainer.style.display = isGame ? 'none' : 'flex'; controlsArea.style.display = isGame ? 'none' : 'block'; gameDashboard.style.display = isGame ? 'flex' : 'none';
            if (isGame) { inputArea.style.display = 'none'; btnOriginal.classList.remove('active'); }
            else {
                if (mode === '通通沒問題') { inputArea.style.display = "flex"; btnOriginal.classList.add('active'); modeDropdown.selectedIndex = 0; }
                else { inputArea.style.display = "none"; btnOriginal.classList.remove('active'); modeDropdown.value = mode; }
            }
            quickActions.innerHTML = '';
            (MODE_ACTIONS[mode] || []).forEach(action => {
                const btn = document.createElement('button'); btn.className = 'action-btn'; btn.innerText = action;
                btn.onclick = () => {
                    if (isProcessing) return;
                    if (action === '猜拳') openRPSGame();
                    else if (action === '修改稱呼') openNamePrompt();
                    else if (action === '專屬稱號') openTitlePrompt();
                    else if (action === '數羊') openSheepCountPrompt();
                    else if (action === '大自然聲音') openNatureSoundPrompt();
                    else if (action === '我要問問題') openQuestionPrompt();
                    else if (action === '五子棋') openGomokuGame();
                    else if (action === '飛鳥大冒險') openBirdGame();
                    else if (action === '夢幻賽車手') openCarGame();
                    else sendMessage(action, true);
                };
                quickActions.appendChild(btn);
            });
            if (mode === '屬於我' && namePromptShownForMode !== mode) { namePromptShownForMode = mode; setTimeout(openNamePrompt, 800); }
        }

        // --- Logic & Network ---
        let audioCtx = null;
        function getCtx() { if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); if (audioCtx.state === 'suspended') audioCtx.resume(); return audioCtx; }
        function playAudioFromUrl(url) { if (!url) return; stopCurrentAudio(); currentAudio = new Audio(url); currentAudio.onended = () => { currentAudio = null; if (nextAudioToPlay) { let t = nextAudioToPlay; nextAudioToPlay = null; playAudioFromUrl(t); } }; currentAudio.play().catch(() => { }); }
        function stopCurrentAudio() { if (currentAudio) { currentAudio.pause(); currentAudio.currentTime = 0; currentAudio = null; } if (abortController) abortController.abort(); }
        function playBeep(sF, eF, d, startTime = null) { const c = getCtx(), n = startTime || c.currentTime, o = c.createOscillator(), g = c.createGain(); o.type = 'sine'; o.frequency.setValueAtTime(sF, n); o.frequency.exponentialRampToValueAtTime(eF, n + d); g.gain.setValueAtTime(0.2, n); g.gain.exponentialRampToValueAtTime(0.01, n + d); o.connect(g); g.connect(c.destination); o.start(n); o.stop(n + d + 0.02); }

        function openNamePrompt() { if (!namePromptModal) namePromptModal = new bootstrap.Modal(document.getElementById('namePromptModal')); namePromptModal.show(); }
        function submitNamePrompt() { const n = document.getElementById('namePromptInput').value.trim(); if (n) { if (namePromptModal) namePromptModal.hide(); fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: `[SET_NAME]${n}`, mode: currentMode, voice_type: voiceSelect.value }) }).then(r => r.json()).then(d => { if (d.reply) { const m = addMessage('bot', d.reply); if (d.audio_url) { attachReplayButton(m, d.audio_url); playAudioFromUrl(d.audio_url); } } }); } }
        function openTitlePrompt() { if (!titlePromptModal) titlePromptModal = new bootstrap.Modal(document.getElementById('titlePromptModal')); titlePromptModal.show(); }
        function sendSetTitle(t) { if (titlePromptModal) titlePromptModal.hide(); fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: `[SET_TITLE]${t}`, mode: currentMode, voice_type: voiceSelect.value }) }).then(r => r.json()).then(d => { if (d.reply) { const m = addMessage('bot', d.reply); if (d.audio_url) { attachReplayButton(m, d.audio_url); playAudioFromUrl(d.audio_url); } } }); }
        function openSheepCountPrompt() { if (!sheepCountModal) sheepCountModal = new bootstrap.Modal(document.getElementById('sheepCountModal')); sheepCountModal.show(); }
        function submitSheepCount() { const c = parseInt(document.getElementById('sheepCountInput').value); if (c > 0 && c <= 100) { if (sheepCountModal) sheepCountModal.hide(); sendMessage(`數 ${c} 隻羊`, true); } }
        function openNatureSoundPrompt() { if (!natureSoundModal) natureSoundModal = new bootstrap.Modal(document.getElementById('natureSoundModal')); natureSoundModal.show(); }
        function playNatureSound(s) { if (natureSoundModal) natureSoundModal.hide(); fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: `大自然${s}`, mode: currentMode, voice_type: voiceSelect.value }) }).then(r => r.json()).then(d => { if (d.reply) { addMessage('bot', d.reply); if (d.next_audio_url) nextAudioToPlay = d.next_audio_url; if (d.audio_url) playAudioFromUrl(d.audio_url); } }); }
        function openQuestionPrompt() { if (!questionPromptModal) questionPromptModal = new bootstrap.Modal(document.getElementById('questionPromptModal')); questionPromptModal.show(); }
        function submitQuestionPrompt() { const q = document.getElementById('questionPromptInput').value.trim(); if (q) { if (questionPromptModal) questionPromptModal.hide(); sendMessage(q, true); } }

        function openGomokuGame() { if (!gomokuModal) gomokuModal = new bootstrap.Modal(document.getElementById('gomokuModal')); gomokuModal.show(); showGomokuSetup(); }
        function showGomokuSetup() { document.getElementById('gomoku-setup').style.display = 'block'; document.getElementById('gomoku-game-area').style.display = 'none'; }
        function startGomoku(mode) { gomokuMode = mode; document.getElementById('gomoku-setup').style.display = 'none'; document.getElementById('gomoku-game-area').style.display = 'block'; document.getElementById('gomoku-mode-display').innerText = mode === 'ai' ? '🤖 挑戰通通' : '👥 雙人對弈'; initGomoku(); }

        function setUILoading(l) { isProcessing = l; [textInput, sendBtn, micBtn, modeDropdown, btnOriginal].forEach(el => { if (el) { if (l) { el.classList.add('opacity-50'); el.style.pointerEvents = 'none'; } else { el.classList.remove('opacity-50'); el.style.pointerEvents = 'auto'; } } }); if (l) { const d = document.createElement('div'); d.id = 'thinking-bubble'; d.className = 'message bot-message'; d.innerHTML = '<span class="spinner-grow spinner-grow-sm me-2"></span>通通正在思考...'; chatContainer.appendChild(d); chatContainer.scrollTop = chatContainer.scrollHeight; } else { const tb = document.getElementById('thinking-bubble'); if (tb) tb.remove(); } }
        async function sendMessage(t, isBtn = false) {
            if (isProcessing) return; const n = t.trim();
            if (currentMode === '好心情' && (n==='擊掌'||n==='跟我擊掌'||n.includes('擊掌'))) { stopCurrentAudio(); triggerHighFiveCelebration(); const s = '合作愉快，我們是最棒的夥伴！'; const m = addMessage('bot', `啪！✋✨ ${s} 🤝💖`); fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: `[RESULT]${s}`, mode: currentMode, voice_type: voiceSelect.value }) }).then(r => r.json()).then(d => { if (d.audio_url) { attachReplayButton(m, d.audio_url); playAudioFromUrl(d.audio_url); } }); return; }
            if (currentMode === '屬於我' && (n==='親親'||n.includes('親親'))) { stopCurrentAudio(); showAffectionAnimation('kiss'); const s = '啾一下送給你，今天也要甜甜的。'; const m = addMessage('bot', s); fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: `[RESULT]${s}`, mode: currentMode, voice_type: voiceSelect.value }) }).then(r => r.json()).then(d => { if (d.audio_url) { attachReplayButton(m, d.audio_url); playAudioFromUrl(d.audio_url); } }); return; }
            if (currentMode === '屬於我' && (n==='抱抱'||n.includes('抱抱'))) { stopCurrentAudio(); showAffectionAnimation('hug'); const s = '來，給你一個大大抱抱。'; const m = addMessage('bot', s); fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: `[RESULT]${s}`, mode: currentMode, voice_type: voiceSelect.value }) }).then(r => r.json()).then(d => { if (d.audio_url) { attachReplayButton(m, d.audio_url); playAudioFromUrl(d.audio_url); } }); return; }
            if (n) addMessage('user', n); setUILoading(true);
            try { abortController = new AbortController(); const r = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: t, mode: currentMode, voice_type: voiceSelect.value }), signal: abortController.signal }); const d = await r.json(); if (d.reply) { const m = addMessage('bot', d.reply); if (d.audio_url) { attachReplayButton(m, d.audio_url); playAudioFromUrl(d.audio_url); } } }
            catch (e) { if (e.name !== 'AbortError') addMessage('bot', '連不上大腦囉...'); } finally { setUILoading(false); }
        }
        function sendMessageFromInput() { const t = textInput.value; if (t.trim()) { sendMessage(t); textInput.value = ''; } }
        textInput.onkeydown = (e) => { if (e.key === 'Enter') sendMessageFromInput(); };

        function addMessage(s, t) { const div = document.createElement('div'); div.className = `message ${s}-message`; if (s === 'bot') { const content = document.createElement('span'); content.className = 'message-content'; const disc = '※ 以上僅供娛樂參考，請理性看待喔！'; const idx = t.indexOf(disc); if (idx !== -1) { content.innerText = t.slice(0, idx).trimEnd(); const sSpan = document.createElement('span'); sSpan.className = 'message-disclaimer'; sSpan.innerText = t.slice(idx); content.appendChild(sSpan); } else { content.innerText = t; } div.appendChild(content); } else { div.innerText = t; } chatContainer.appendChild(div); chatContainer.scrollTop = chatContainer.scrollHeight; return div; }
        function attachReplayButton(el, url) { const b = document.createElement('button'); b.className = 'replay-audio-btn'; b.innerText = '🔊'; b.onclick = () => playAudioFromUrl(url); el.appendChild(b); }
        function switchToOriginal() { window.location.href = "/?mode=通通沒問題&voice=" + voiceSelect.value; }
        function switchToPersonality() { window.location.href = "/?mode=" + modeDropdown.value + "&voice=" + voiceSelect.value; }
        function switchToGameZone() { window.location.href = "/?mode=遊戲專區&voice=" + voiceSelect.value; }

        // Gomoku Game Logic (Simplified)
        let gomokuBoard = [], gomokuCurrentPlayer = 1, gomokuGameOver = false, gomokuMode = 'friend', gomokuListenerAttached = false;
        const gomokuGridSize = 15, gomokuCellSize = 25, gomokuPadding = 25;
        function initGomoku() { 
            const c = document.getElementById('gomokuCanvas');
            if (!gomokuListenerAttached) {
                c.addEventListener('click', handleGomokuClick);
                gomokuListenerAttached = true;
            }
            gomokuBoard = Array(15).fill().map(() => Array(15).fill(0)); 
            gomokuCurrentPlayer = 1; 
            gomokuGameOver = false; 
            updateGomokuInfo(); 
            drawGomokuBoard(); 
        }
        function drawGomokuBoard() { const c = document.getElementById('gomokuCanvas'), ctx = c.getContext('2d'); ctx.clearRect(0, 0, 400, 400); ctx.strokeStyle = '#8B4513'; for (let i = 0; i < 15; i++) { ctx.beginPath(); ctx.moveTo(25, 25 + i * 25); ctx.lineTo(375, 25 + i * 25); ctx.stroke(); ctx.beginPath(); ctx.moveTo(25 + i * 25, 25); ctx.lineTo(25 + i * 25, 375); ctx.stroke(); } for (let y = 0; y < 15; y++) for (let x = 0; x < 15; x++) if (gomokuBoard[y][x]) { const px = 25 + x * 25, py = 25 + y * 25; ctx.beginPath(); ctx.arc(px, py, 10, 0, Math.PI * 2); ctx.fillStyle = gomokuBoard[y][x] === 1 ? '#000' : '#fff'; ctx.fill(); ctx.stroke(); } }
        function updateGomokuInfo() { document.getElementById('gomoku-info').innerText = `輪到：${gomokuCurrentPlayer === 1 ? "黑棋" : (gomokuMode === 'ai' ? "通通" : "白棋")}`; }
        function handleGomokuClick(e) { if (gomokuGameOver || (gomokuMode === 'ai' && gomokuCurrentPlayer === 2)) return; const c = document.getElementById('gomokuCanvas'), r = c.getBoundingClientRect(), x = Math.round((e.clientX - r.left - 25) / 25), y = Math.round((e.clientY - r.top - 25) / 25); if (x >= 0 && x < 15 && y >= 0 && y < 15 && !gomokuBoard[y][x]) { 
            gomokuBoard[y][x] = gomokuCurrentPlayer; 
            playBeep(600, 450, 0.05); // 玩家落子音效
            drawGomokuBoard(); 
            if (checkWin(x, y)) { gomokuGameOver = true; playWinMelody(); sendMessage(`[RESULT]${gomokuMode==='ai'?(gomokuCurrentPlayer===1?"你贏過通通了！":"通通贏囉！"):("恭喜獲勝！")}`, true); return; } gomokuCurrentPlayer = 3 - gomokuCurrentPlayer; updateGomokuInfo(); if (gomokuMode === 'ai') setTimeout(aiMove, 600); } }
        function aiMove() {
            let bestScore = -1, bx = 7, by = 7;
            const size = 15;
            
            // 遍歷棋盤上所有空格，計算評分
            for (let y = 0; y < size; y++) {
                for (let x = 0; x < size; x++) {
                    if (gomokuBoard[y][x] === 0) {
                        // 評估該位置對「通通(2)」的進攻分數，以及對「玩家(1)」的防禦分數
                        let score = evaluatePosition(x, y, 2) + evaluatePosition(x, y, 1);
                        
                        // 加入些微隨機性，避免每次開局走法都一模一樣
                        score += Math.random() * 2;

                        if (score > bestScore) {
                            bestScore = score;
                            bx = x;
                            by = y;
                        }
                    }
                }
            }

            gomokuBoard[by][bx] = 2;
            playBeep(500, 350, 0.05); // 通通落子音效
            drawGomokuBoard();
            
            if (checkWin(bx, by)) {
                gomokuGameOver = true;
                playRpsTone('lose');
                sendMessage("[RESULT]嘿嘿！這局是通通贏囉！你要再接再厲喔！😜🏆", true);
                return;
            }
            
            gomokuCurrentPlayer = 1;
            updateGomokuInfo();
        }

        function evaluatePosition(x, y, player) {
            let totalScore = 0;
            const directions = [[1, 0], [0, 1], [1, 1], [1, -1]];
            
            for (let [dx, dy] of directions) {
                let count = 1;
                let block = 0;
                
                // 正向檢查
                let tx = x + dx, ty = y + dy;
                while (tx >= 0 && tx < 15 && ty >= 0 && ty < 15 && gomokuBoard[ty][tx] === player) {
                    count++; tx += dx; ty += dy;
                }
                if (!(tx >= 0 && tx < 15 && ty >= 0 && ty < 15 && gomokuBoard[ty][tx] === 0)) block++;
                
                // 反向檢查
                tx = x - dx; ty = y - dy;
                while (tx >= 0 && tx < 15 && ty >= 0 && ty < 15 && gomokuBoard[ty][tx] === player) {
                    count++; tx -= dx; ty -= dy;
                }
                if (!(tx >= 0 && tx < 15 && ty >= 0 && ty < 15 && gomokuBoard[ty][tx] === 0)) block++;

                // 評分權重
                if (count >= 5) totalScore += 100000;
                else if (count === 4) {
                    if (block === 0) totalScore += 10000; // 活四
                    else if (block === 1) totalScore += 1000; // 衝四
                }
                else if (count === 3) {
                    if (block === 0) totalScore += 500; // 活三
                    else if (block === 1) totalScore += 100; // 眠三
                }
                else if (count === 2) {
                    if (block === 0) totalScore += 50;
                }
            }
            return totalScore;
        }
        function checkWin(x, y) { const p = gomokuBoard[y][x]; for (let [dx, dy] of [[1, 0], [0, 1], [1, 1], [1, -1]]) { let c = 1; for (let s of [1, -1]) { let tx = x + dx * s, ty = y + dy * s; while (tx >= 0 && tx < 15 && ty >= 0 && ty < 15 && gomokuBoard[ty][tx] === p) { c++; tx += dx * s; ty += dy * s; } } if (c >= 5) return true; } return false; }
        function playWinMelody() { const c = getCtx(), n = c.currentTime; [523, 659, 783, 1046].forEach((f, i) => playBeep(f, f, 0.3, n + i * 0.1)); }

        // Start
        currentMode = "通通沒問題" || '通通沒問題';
        updateUIForMode(currentMode);
        const initialMsg = "\u2728 \u6a21\u5f0f\u5df2\u5207\u63db\u70ba\uff1a\u3010\u901a\u901a\u6c92\u554f\u984c\u3011 \u2728 \u6211\u662f\u6700\u5f37\u5927\u7684\u901a\u901a\uff01\u6709\u4ec0\u9ebc\u554f\u984c\u4ea4\u7d66\u6211\u5c31\u5c0d\u4e86\uff0c\u901a\u901a\u6c92\u554f\u984c\uff01\ud83e\udd16\ud83d\udcaa";
        const initialAudio = "/static/audio/voice_4787cf99-022d-429f-9af2-b3062b5db18b.mp3";
        if (initialMsg && initialMsg !== "" && initialMsg !== "None") { const m = addMessage('bot', initialMsg); if (initialAudio && initialAudio !== "" && initialAudio !== "None") { attachReplayButton(m, initialAudio); playAudioFromUrl(initialAudio); } }
        setInterval(() => fetch('/api/cleanup', { method: 'POST' }), 600000);
    
} catch(e) { console.error('RUNTIME ERROR:', e); process.exit(1); }