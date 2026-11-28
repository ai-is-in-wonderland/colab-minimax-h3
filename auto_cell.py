# おまかせのセル（MiniMax H3・口合わせ・全カット自動）AI is in Wonderland
# 使い方：ランタイムのタイプを G4（なければ A100）にして、下の SET を自分の素材の組の名前にし、▶ を1回押す → ドライブの許可だけ押す。あとは触らない。
# 準備 → 全カットを作る → 1本できるたびにドライブへ → 最後に自分でランタイムを止める。途中で止まったら、もう一度押せば続きから（できた分は飛ばす）。
SET = 'sample'          # 素材の組（マイドライブ/AI_Colab/H3/inputs/<SET>/<カット>/ に start.png・voice.wav・prompt.txt）
MAX_MIN = 90            # これを過ぎたら、何をしていても止める（ユニットを守る）
STOP_AT_END = True      # 終わったらランタイムを止める
import os, re, json, time, shutil, subprocess, threading, urllib.request, urllib.error, uuid, glob
T0 = time.time()
from google.colab import drive, runtime
drive.mount('/content/drive')
BASE = '/content/drive/MyDrive/AI_Colab/H3'
IN = f'{BASE}/inputs/{SET}'
os.environ['TZ'] = 'Asia/Tokyo'; time.tzset()   # フォルダの名前を日本の時刻に
OUT = f"{BASE}/output/{time.strftime('%Y%m%d_%H%M')}_auto"
prev = sorted(glob.glob(f'{BASE}/output/*_auto/_STATUS.txt'))
if prev and '終わり' not in open(prev[-1], encoding='utf-8').read():
    OUT = os.path.dirname(prev[-1])          # 前の回が途中なら、同じフォルダで続きから
os.makedirs(OUT, exist_ok=True)
def status(msg):
    line = time.strftime('%H:%M:%S') + ' ' + msg
    print(line)
    open(f'{OUT}/_STATUS.txt', 'a', encoding='utf-8').write(line + '\n')
def stop(why):
    status('止める：' + why)
    if STOP_AT_END:
        time.sleep(3)
        runtime.unassign()
RUN_ID = T0
def watchdog(my=RUN_ID):
    while time.time() - T0 < MAX_MIN * 60:
        time.sleep(30)
        if globals().get('RUN_ID') != my:
            return
    stop(f'時間切れ（{MAX_MIN}分）')
threading.Thread(target=watchdog, daemon=True).start()
def sh(cmd, timeout=1800):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
try:
    # 1. GPU
    q = sh(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'], 60).stdout.strip()
    if not q or int(re.sub(r'\D', '', q.split(',')[1]) or 0) < 70 * 1024:
        raise RuntimeError('GPU が足りない（' + (q or 'なし') + '）。ランタイムのタイプを G4 か A100 にして、もう一度')
    status('GPU：' + q)
    # 2. ComfyUI と PyTorch
    WHL = 'nvidia_cublas-13.1.1.3-py3-none-manylinux_2_27_x86_64.whl'
    if not os.path.exists('/content/ComfyUI/main.py'):
        sh(['git', 'clone', '-q', 'https://github.com/Comfy-Org/ComfyUI', '/content/ComfyUI'])
    sh(['pip', '-q', 'install', '-r', '/content/ComfyUI/requirements.txt'])
    for _ in range(10):
        sh(['curl', '-sL', '-C', '-', '--retry', '20', '--retry-all-errors', '-o', f'/tmp/{WHL}', 'https://pypi.nvidia.com/nvidia-cublas/' + WHL])
        if os.path.exists(f'/tmp/{WHL}') and os.path.getsize(f'/tmp/{WHL}') >= 420_000_000:
            break
    sh(['pip', 'install', '-q', f'/tmp/{WHL}'])
    sh(['pip', '-q', 'install', '--upgrade', 'torch', 'torchvision', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cu130'])
    sh(['pip', '-q', 'install', 'huggingface_hub[hf_xet]'])
    if not re.search(r'Version:\s*13\.1', sh(['pip', 'show', 'nvidia-cublas']).stdout):
        sh(['pip', 'install', '-q', '--no-deps', '--force-reinstall', f'/tmp/{WHL}'])
    status('ComfyUI と PyTorch を入れた')
    # 3. モデル
    os.environ['HF_XET_HIGH_PERFORMANCE'] = '1'
    from huggingface_hub import hf_hub_download
    M = '/content/ComfyUI/models'
    FILES = [('diffusion_models', 'minimax_h3_fastvideo_vsa_datafree_1300step_4step_int8_convrot.safetensors', 'Kijai/MiniMax-H3-experimental', 'minimax_h3_fastvideo_vsa_datafree_1300step_4step_int8_convrot.safetensors', 22.9),
             ('vae', 'minimax_h3_video_vae_int8_convrot.safetensors', 'Kijai/MiniMax-H3-experimental', 'minimax_h3_video_vae_int8_convrot.safetensors', 3.17),
             ('text_encoders', 'qwen3vl_32b_minimax_h3_int8_convrot.safetensors', 'Comfy-Org/MiniMax-H3', 'text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors', 27.14),
             ('vae', 'minimax_h3_audio_vae_fp32.safetensors', 'Comfy-Org/MiniMax-H3', 'vae/minimax_h3_audio_vae_fp32.safetensors', 0.61)]
    for sub, name, repo, path, want in FILES:
        dst = f'{M}/{sub}/{name}'
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        for _ in range(3):
            if os.path.exists(dst) and os.path.getsize(dst) / 1e9 > want * 0.95:
                break
            try:
                shutil.move(hf_hub_download(repo, path, local_dir='/content/hf_tmp'), dst)
            except Exception as e:
                status('モデルの取り直し：' + name + ' ' + str(e)[:80])
        if not (os.path.exists(dst) and os.path.getsize(dst) / 1e9 > want * 0.95):
            raise RuntimeError('モデルが入らない：' + name)
    status('モデル4本がそろった')
    # 4. 素材のフォルダ → 仕事の一覧（長さは声から）
    urllib.request.urlretrieve('https://raw.githubusercontent.com/ai-is-in-wonderland/colab-minimax-h3/main/h3_job_patch.py', '/content/h3_job_patch.py')
    exec(open('/content/h3_job_patch.py', encoding='utf-8').read())
    jobs = []
    for J in sorted(j for j in os.listdir(IN) if os.path.isdir(f'{IN}/{j}')):
        try:
            d, cut = load_cut(IN, J)
            for k, f in (('img', cut['images'][0]), ('aud', cut['audio'])):
                shutil.copy(f'{d}/{f}', f'/content/ComfyUI/input/{J}_{f}')
            jobs.append(dict(id=J, img=f"{J}_{cut['images'][0]}", aud=f"{J}_{cut['audio']}", prompt=open(f"{d}/{cut['prompt']}", encoding='utf-8').read().strip(),
                             frames=round(float(cut['seconds']) * 24), steps=int(cut['steps']), seed=int(cut.get('seed', 1))))
        except Exception as e:
            status(f'{J}：素材がそろっていない → 飛ばす（{e}）')
    if not jobs:
        raise RuntimeError(f'カットが無い：{IN} に、カットごとのフォルダ（start.png・voice.wav・prompt.txt）を入れる')
    status(f'カット {len(jobs)} 本：' + ', '.join(j['id'] for j in jobs))
    # 5. ComfyUI を画面なしで起動
    HOST = 'http://127.0.0.1:8188'
    proc = subprocess.Popen(['python', 'main.py', '--listen', '127.0.0.1', '--port', '8188'], cwd='/content/ComfyUI', stdout=open('/content/comfy.log', 'w'), stderr=subprocess.STDOUT)
    for _ in range(240):
        time.sleep(2)
        try:
            urllib.request.urlopen(HOST + '/system_stats', timeout=5)
            break
        except Exception:
            pass
    else:
        raise RuntimeError('ComfyUI が起動しない（/content/comfy.log）')
    get = lambda p, t=30: json.load(urllib.request.urlopen(HOST + p, timeout=t))
    def post(p, body, t=60):
        return urllib.request.urlopen(urllib.request.Request(HOST + p, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}), timeout=t)
    info = get('/object_info', 120)
    def fill(cls, want):   # この ComfyUI にある入力だけ・足りない入力は既定の値
        i = info.get(cls, {}).get('input', {})
        spec = {**i.get('required', {}), **i.get('optional', {})}
        use = {k: v for k, v in want.items() if k in spec or isinstance(v, list) or '.' in k}
        for k, s in spec.items():
            if k in use or not isinstance(s[0], (str, list)):
                continue
            if isinstance(s[0], str) and s[0] not in ('INT', 'FLOAT', 'STRING', 'BOOLEAN', 'COMBO'):
                continue
            if len(s) > 1 and isinstance(s[1], dict) and 'default' in s[1]:
                use[k] = s[1]['default']
            elif isinstance(s[0], list) and s[0]:
                use[k] = s[0][0]
        return use
    def build(j):
        g = {}
        def add(nid, ct, inputs):
            g[nid] = {'class_type': ct, 'inputs': fill(ct, inputs)}
            return [nid, 0]
        m = add('1', 'UNETLoader', {'unet_name': FILES[0][1], 'weight_dtype': 'default'})
        m = add('2', 'MiniMaxH3SigmaShift', {'model': m, 'shift_video': 12.0, 'shift_audio': 3.0})
        m = add('3', 'ModelAttentionBackend', {'model': m, 'attention': 'comfy kitchen attention'})
        m = add('4', 'BlockSparseAttention', {'model': m, 'selection': 'vsa', 'selection.keep_percent': 10.0, 'start_percent': 0.2, 'end_percent': 1.0,
                                             'dense_blocks': '', 'min_tokens': 12288, 'extra_tokens': 256, 'sink_conditioning': 'exact_kv_and_rows', 'verbose': False})
        add('10', 'CLIPLoader', {'clip_name': FILES[2][1], 'type': 'minimax', 'device': 'default'})
        add('12', 'VAELoader', {'vae_name': FILES[1][1]})
        add('14', 'VAELoader', {'vae_name': FILES[3][1]})
        add('16', 'LoadImage', {'image': j['img']})
        add('17', 'ImageScale', {'image': ['16', 0], 'upscale_method': 'lanczos', 'width': 1536, 'height': 864, 'crop': 'center'})
        add('20', 'MiniMaxH3ImageToVideo', {'clip': ['10', 0], 'vae': ['12', 0], 'first_frame': ['17', 0], 'prompt': j['prompt'], 'width': 1536, 'height': 864, 'length': j['frames']})
        add('38', 'LoadAudio', {'audio': j['aud']})
        add('39', 'VAEEncodeAudio', {'audio': ['38', 0], 'vae': ['14', 0]})
        add('40', 'SolidMask', {'value': 0.0, 'width': 32, 'height': 32})
        add('41', 'SetLatentNoiseMask', {'samples': ['39', 0], 'mask': ['40', 0]})
        add('42', 'LTXVConcatAVLatent', {'video_latent': ['20', 1], 'audio_latent': ['41', 0]})
        add('45', 'RandomNoise', {'noise_seed': j['seed']})
        add('46', 'KSamplerSelect', {'sampler_name': 'er_sde'})
        add('47', 'BasicScheduler', {'model': m, 'scheduler': 'simple', 'steps': j['steps'], 'denoise': 1.0})
        add('48', 'BasicGuider', {'model': m, 'conditioning': ['20', 0]})
        add('49', 'SamplerCustomAdvanced', {'noise': ['45', 0], 'guider': ['48', 0], 'sampler': ['46', 0], 'sigmas': ['47', 0], 'latent_image': ['42', 0]})
        add('50', 'VAEDecode', {'samples': ['49', 0], 'vae': ['12', 0]})
        add('53', 'CreateVideo', {'images': ['50', 0], 'audio': ['38', 0], 'fps': 24.0})
        add('54', 'SaveVideo', {'video': ['53', 0], 'filename_prefix': 'H3auto/' + j['id'], 'format': 'auto', 'codec': 'auto'})
        return g
    # 6. 1本ずつ作って、できたらすぐドライブへ
    for n, j in enumerate(jobs, 1):
        if os.path.exists(f"{OUT}/{j['id']}.mp4"):
            status(f"[{n}/{len(jobs)}] {j['id']}：もうできている → 飛ばす"); continue
        t = time.time()
        try:
            pid = json.load(post('/prompt', {'prompt': build(j), 'client_id': str(uuid.uuid4())}))['prompt_id']
        except urllib.error.HTTPError as e:
            status(f"[{n}/{len(jobs)}] {j['id']}：断られた " + e.read().decode('utf-8', 'replace')[:300]); continue
        out, err, silent = {}, None, 0
        while True:
            time.sleep(3)
            try:
                h = get('/history/' + pid); silent = 0
            except Exception:
                h = {}; silent += 1
                if silent > 20:
                    err = 'ComfyUI が返事をしない'; break
            if pid in h:
                s = h[pid].get('status', {})
                if s.get('status_str') == 'error':
                    err = json.dumps(s.get('messages', []), ensure_ascii=False)[-400:]
                out = h[pid].get('outputs', {}); break
            if time.time() - t > 900:
                err = '15分たっても終わらない'
                post('/interrupt', {}); post('/queue', {'clear': True}); break
        files = [f for nd in out.values() for k in ('video', 'images', 'gifs') for f in (nd.get(k) or [])]
        if files:
            f = files[0]
            shutil.copy(os.path.join('/content/ComfyUI/output', f.get('subfolder') or '', f['filename']), f"{OUT}/{j['id']}.mp4")
        json.dump({'id': j['id'], 'seconds': round(time.time() - t, 1), 'frames': j['frames'], 'error': err}, open(f"{OUT}/{j['id']}.json", 'w'), ensure_ascii=False)
        status(f"[{n}/{len(jobs)}] {j['id']}：" + (f'NG {err}' if err or not files else f'{round(time.time() - t)}秒 → ドライブへ保存'))
        if err == 'ComfyUI が返事をしない':
            break
    status(f'終わり（{round((time.time() - T0) / 60)}分）。動画は ' + OUT.replace('/content/drive/MyDrive/', 'マイドライブ/'))
    stop('全部終わった')
except Exception as e:
    status('NG：' + str(e)[:300])
    stop('止まったので、ユニットを守るために止める（もう一度押せば続きから）')
