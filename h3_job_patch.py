# -*- coding: utf-8 -*-
"""MiniMax H3 on Google Colab: turn one cut folder into a ComfyUI workflow (AI is in Wonderland, 2026-11).
A cut folder holds:  start.png (the first frame), voice.wav (the dialogue for lip-sync), prompt.txt (the H3 prompt)
and optionally cut.json: {"mode": "frame", "seconds": 7.0, "steps": 4, "seed": 1, "images": ["start.png"],
"audio": "voice.wav", "prompt": "prompt.txt"}.  Without cut.json the length is taken from voice.wav (+0.6 s),
mode frame, 4 steps.  frames = round(seconds * 24).  H3 VIDEO only."""
import json
import os
import shutil

NODE = dict(mode=1, size=2, motion=3, lipsync=4, seconds=13, frames=14, img=(16, 17, 18, 21), audio=38, seed=45, prompt_ref=55, prompt_frame=56, save=112)


def drop_link(wf, lid):
    """remove one link from the UI-format workflow (links list, the target input and the origin output)"""
    wf['links'] = [l for l in wf['links'] if l[0] != lid]
    for n in wf['nodes']:
        for x in n.get('inputs', []) or []:
            if x.get('link') == lid:
                x['link'] = None
        for o in n.get('outputs', []) or []:
            if o.get('links') and lid in o['links']:
                o['links'] = [k for k in o['links'] if k != lid]


def load_cut(inp, job):
    d = f'{inp}/{job}'
    if not os.path.isdir(d):
        raise ValueError(f'入力のフォルダが無い: {d}')
    cj = f'{d}/cut.json'
    cut = json.load(open(cj, encoding='utf-8')) if os.path.exists(cj) else {}
    cut.setdefault('mode', 'frame')
    cut.setdefault('steps', 4)
    cut.setdefault('seed', 1)
    cut.setdefault('images', ['start.png'])
    cut.setdefault('audio', 'voice.wav')
    cut.setdefault('prompt', 'prompt.txt')
    if 'seconds' not in cut:   # 長さは声から（声の長さ＋0.6 秒）
        import wave
        try:
            with wave.open(f"{d}/{cut['audio']}") as wf:
                cut['seconds'] = round(wf.getnframes() / wf.getframerate() + 0.6, 3)
        except Exception as e:
            raise ValueError(f"声のファイルが読めない（{cut['audio']}・WAV にしてください）: {e}")
    miss = [k for k in ('mode', 'seconds', 'steps', 'images', 'audio', 'prompt') if k not in cut or cut[k] in (None, '', [])]
    if miss:
        raise ValueError('足りない項目: ' + ', '.join(miss))
    if cut['mode'] not in ('frame', 'ref'):
        raise ValueError("mode は 'frame' か 'ref'")
    if cut['steps'] not in (4, 8):
        raise ValueError('steps は 4 か 8')
    if cut['mode'] == 'ref' and len(cut['images']) > 4:
        raise ValueError('ref の画像は最大 4 枚')
    for f in list(cut['images']) + [cut['audio'], cut['prompt']]:
        if not os.path.exists(f'{d}/{f}'):
            raise ValueError(f'ファイルが無い: {d}/{f}')
    return d, cut


def patch(template, d, cut, job, comfy_input):
    """returns (patched workflow dict, info dict). Copies the images/audio into ComfyUI/input under job-prefixed names."""
    wf = json.loads(json.dumps(template))
    byid = {n['id']: n for n in wf['nodes']}
    os.makedirs(comfy_input, exist_ok=True)

    def put(fname):
        dst = f'{job}_{fname}'
        shutil.copy(f'{d}/{fname}', f'{comfy_input}/{dst}')
        return dst
    imgs = [put(f) for f in cut['images']]
    aud = put(cut['audio'])
    prompt = open(f"{d}/{cut['prompt']}", encoding='utf-8').read().strip()
    frames = round(float(cut['seconds']) * 24)
    # unused picture slots point at the first image (a missing file would stop the validation)
    slots = list(imgs) + [imgs[0]] * (4 - len(imgs))
    byid[NODE['mode']]['widgets_values'] = [cut['mode'] == 'frame']
    byid[NODE['size']]['widgets_values'] = [True]      # 1536x864
    byid[NODE['motion']]['widgets_values'] = [cut['steps'] == 8]
    byid[NODE['lipsync']]['widgets_values'] = [True]
    byid[NODE['seconds']]['widgets_values'] = [float(cut['seconds'])]
    byid[NODE['frames']]['widgets_values'] = [str(frames)]
    for nid, f in zip(NODE['img'], slots):
        byid[nid]['widgets_values'] = [f, 'image']
    byid[NODE['audio']]['widgets_values'] = [aud, None]
    byid[NODE['seed']]['widgets_values'] = [int(cut.get('seed', 2026112100)), 'fixed']
    byid[NODE['prompt_frame' if cut['mode'] == 'frame' else 'prompt_ref']]['widgets_values'] = [prompt]
    # frame mode: the template wires image node 17 into MiniMaxH3ImageToVideo.last_frame - that would force every cut to END on its first frame
    n24 = byid[24]
    lf_idx = next(i for i, x in enumerate(n24['inputs']) if x['name'] == 'last_frame')
    lf_link = n24['inputs'][lf_idx].get('link')
    last = cut.get('last_frame')
    if cut['mode'] == 'frame':
        if last:
            if not os.path.exists(f'{d}/{last}'):
                raise ValueError(f'last_frame のファイルが無い: {d}/{last}')
            byid[17]['widgets_values'] = [put(last), 'image']
        elif lf_link is not None:
            drop_link(wf, lf_link)
    byid[NODE['save']]['widgets_values'] = [f'H3/{job}', 'auto', 'auto']
    return wf, dict(job=job, mode=cut['mode'], seconds=cut['seconds'], frames=frames, steps=cut['steps'], images=imgs, audio=aud, prompt_chars=len(prompt), last_frame=bool(cut['mode'] == 'frame' and last))
